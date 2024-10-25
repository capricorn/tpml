from typing import List, Tuple, Union

from parser import ast
from lexer import lex
from lexer import token

class ParseError(Exception):
    ...

def consume_balanced_token(left_match: token.Token, right_match: token.Token, tokens: List[token.Token]) -> Tuple[List[token.Token], List[token.Token]]:
    ''' Return the body of a balanced token and the remainder after it. '''

    assert len(tokens) >= 2
    if tokens[0] != left_match:
        raise ParseError()

    stack = 0
    body = None
    for i in range(len(tokens)):
        tok = tokens[i]
        if isinstance(tok, type(left_match)):
            stack += 1
        elif isinstance(tok, type(right_match)):
            stack -= 1
            if stack == 0:
                body = tokens[1:i]
                break
    
    if body is None:
        raise ParseError()
    
    return (body, tokens[i+1:])

def parse_ellipsis(tokens: List[token.Token]) -> Tuple[ast.Ellipsis, List[token.Token]]:
    if len(tokens) == 0:
        raise ParseError()

    if isinstance(tokens[0], token.Ellipsis):
        return [ast.Ellipsis(), tokens[1:]]
    
    raise ParseError()

def parse_string(tokens: List[token.Token]) -> Tuple[ast.String, List[token.Token]]:
    if len(tokens) == 0:
        raise ParseError()

    if isinstance(tokens[0], token.String):
        return [ast.String(value=tokens[0].value), tokens[1:]]

    raise ParseError()

def parse_tag(tokens: List[token.Token]) -> Tuple[str, List[token.Token]]:
    if len(tokens) == 0:
        raise ParseError()
    
    if isinstance(tokens[0], token.TagName) or isinstance(tokens[0], token.Wildcard):
        return (tokens[0].name, tokens[1:])

    raise ParseError()

def parse_variable(tokens: List[token.Token]) -> Tuple[str, List[token.Token]]:
    if len(tokens) == 0:
        raise ParseError()
    
    if isinstance(tokens[0], token.Variable):
        return (tokens[0].name, tokens[1:])

    raise ParseError()

def parse_comma_delim(tokens: List[token.Token]) -> List[token.Token]:
    if len(tokens) == 0:
        raise ParseError()
    if not isinstance(tokens[0], token.CommaDelimiter):
        raise ParseError()
    
    return tokens[1:]

def parse_colon(tokens: List[token.Token]) -> List[token.Token]:
    if len(tokens) == 0:
        raise ParseError('Expected colon')
    if not isinstance(tokens[0], token.Colon):
        raise ParseError('Expected colon')
    
    return tokens[1:]

def consume_unification(tokens: List[token.Token]) -> List[token.Token]:
    if len(tokens) == 0:
        raise ParseError()
    if not isinstance(tokens[0], token.Unification):
        raise ParseError()
    
    return tokens[1:]

def parse_set(tokens: List[token.Token]) -> Tuple[ast.Set, List[token.Token]]:
    body, remainder = consume_balanced_token(left_match=token.LeftBrace(), right_match=token.RightBrace(), tokens=tokens)

    body_types = [ type(token) for token in body ]
    members = []
    while body_types != []:
        match body_types:
            case [ token.String ]:
                string, body = parse_string(body)
                body_types = [ type(tok) for tok in body ]
                members.append(string)
            case [ token.Ellipsis ]:
                ellipsis, body = parse_ellipsis(body)
                body_types = [ type(tok) for tok in body ]
                members.append(ellipsis)
            case [ token.String, token.CommaDelimiter, *_ ]:
                string, body = parse_string(body)
                body = parse_comma_delim(body)
                body_types = [ type(tok) for tok in body ]
                members.append(string)
            case [ token.Ellipsis, token.CommaDelimiter, *_ ]:
                ellipsis, body = parse_ellipsis(body)
                body = parse_comma_delim(body)
                body_types = [ type(tok) for tok in body ]
                members.append(ellipsis)
            case _:
                raise ParseError(f'Unexpected sequence when parsing set: {body}')

    return [ast.Set(members=members), remainder]

def parse_dict(tokens: List[token.Token]) -> Tuple[ast.Dict, List[token.Token]]:
    body, remainder = consume_balanced_token(left_match=token.LeftBrace(), right_match=token.RightBrace(), tokens=tokens)
    body_types = [ type(tok) for tok in body ]
    values = []

    while body_types != []:
        match body_types:
            case [token.String, token.Colon, token.String]:
                key, body = parse_string(body)
                body = parse_colon(body)
                value, body = parse_string(body)
                values.append((key,value))
            case [token.String, token.Colon, token.LeftBrace, _, *_]:
                # TODO: Different pattern matching lib to handle this
                key, body = parse_string(body)
                body = parse_colon(body)
                value_set, body = parse_set(body)
                values.append((key, value_set))

                if len(body) > 1 and type(body[0]) == token.CommaDelimiter:
                    body = parse_comma_delim(body)
            case [token.String, token.Colon, token.String, token.CommaDelimiter, _, *_]:
                key, body = parse_string(body)
                body = parse_colon(body)
                value, body = parse_string(body)
                body = parse_comma_delim(body)
                values.append((key,value))
            case _:
                raise ParseError(f'Unexpected sequence when parsing dict: {body}')
        
        body_types = [ type(tok) for tok in body ]
    
    return (ast.Dict(members=values), remainder)
    
def parse_attributes(tokens: List[token.Token]) -> Tuple[List[ast.HTMLAttribute], List[token.Token]]:
    # TODO: Correctly parse
    body, tokens = consume_balanced_token(token.LeftBracket(), token.RightBracket(), tokens)
    return body, tokens

def parse_children(tokens: List[token.Token]) -> Tuple[List[ast.HTMLNode], List[token.Token]]:
    assert len(tokens) > 0

    if isinstance(tokens[0], token.Variable):
        # TODO: Should really return the var ast here
        name, remainder = parse_variable(tokens)
        return [ast.HTMLNode(tag=name, attrs=[], children=[])], remainder
    # TODO: Should really treat wildcard as a variable
    elif isinstance(tokens[0], token.Wildcard):
        name, remainder = parse_tag(tokens)
        return [ast.HTMLNode(tag=name, attrs=[], children=[])], remainder

    body, remainder = consume_balanced_token(token.LeftBracket(), token.RightBracket(), tokens)
    nodes = []
    # In this body, parse all nodes.
    while body != []:
        node, body = parse_node(body)
        nodes.append(node)
        if body != []:
            body = parse_comma_delim(body)

    return nodes, remainder

def parse_node(tokens: List[token.Token]) -> Tuple[ast.HTMLNode, List[token.Token]]:
    body, remainder = consume_balanced_token(token.LeftParen(), token.RightParen(), tokens)

    if body == []:
        return ast.HTMLNode(tag=None, attrs=[], children=[]), remainder

    if isinstance(body[0], token.Variable):
        tag, body = parse_variable(body)
    elif isinstance(body[0], token.TagName) or isinstance(body[0], token.Wildcard):
        tag, body = parse_tag(body)
    else:
        raise ParseError(f'Expected tag name or variable; got {body[0]}')

    body = parse_comma_delim(body)
    attrs, body = parse_attributes(body)    # [] literal for now.
    body = parse_comma_delim(body)
    children, body = parse_children(body)

    return ast.HTMLNode(tag=tag, attrs=attrs, children=children), remainder

def parse_unification(tokens: List[token.Token]) -> ast.NodeUnification:
    left_node, tokens = parse_node(tokens)
    tokens = consume_unification(tokens)
    right_node, tokens = parse_node(tokens)

    return ast.NodeUnification(left=left_node, right=right_node)

def parse(input: str) -> ast.HTMLNode:
    tokens = lex.lex(input)
    # Initially, _only_ parse nodes of the form (tag,[],[])
    node, _ = parse_node(tokens)
    return node

