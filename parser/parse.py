from typing import List, Tuple, Union

from parser import ast
from lexer import lex
from lexer import token

DictValue = Union[ast.String, ast.Wildcard, ast.Set]
DictKey = ast.String
DictEntry = Union[ast.Ellipsis, Tuple[DictKey, DictValue]]

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

def parse_wildcard(tokens: List[token.Token]) -> Tuple[ast.Wildcard, List[token.Token]]:
    if tokens == []:
        raise ParseError('Failed to parse wildcard: empty token list.')
    
    if type(tokens[0]) != token.Wildcard:
        raise ParseError(f'Failed to parse wildcard: bad token {tokens[0]}')
    
    return (ast.Wildcard(), tokens[1:])

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

def parse_dict_key(tokens: List[token.Token]) -> Tuple[DictKey, List[token.Token]]:
    return parse_string(tokens)

def parse_dict_value(tokens: List[token.Token]) -> Tuple[DictValue, List[token.Token]]:
    try:
        return parse_string(tokens)
    except ParseError:
        ...
    
    try:
        return parse_wildcard(tokens)
    except ParseError:
        ...
    
    try:
        return parse_set(tokens)
    except ParseError:
        ...
    
    raise ParseError(f'Failed to parse dict value from tokens {tokens}')

def parse_dict_entry(tokens: List[token.Token]) -> Tuple[DictEntry, List[token.Token]]:
    try:
        return parse_ellipsis(tokens)
    except:
        ...

    # WIP: Attempt unpack parsing here
    try:
        return parse_unpack_operator(tokens)
    except:
        ...

    try:
        key, tokens = parse_dict_key(tokens)
        tokens = parse_colon(tokens)
        value, tokens = parse_dict_value(tokens)
        return ((key,value), tokens)
    except:
        ...

    raise ParseError(f'Failed to parse dict entry from tokens {tokens}')

def parse_dict(tokens: List[token.Token]) -> Tuple[ast.Dict, List[token.Token]]:
    body, remainder = consume_balanced_token(left_match=token.LeftBrace(), right_match=token.RightBrace(), tokens=tokens)
    values = []

    while body != []:
        val, body = parse_dict_entry(body)
        values.append(val)

        if body != []:
            body = parse_comma_delim(body)
            if body == []:
                raise ParseError('Failed to parse dict: trailing comma')
    
    return (ast.Dict(members=values), remainder)
    
def parse_attributes(tokens: List[token.Token]) -> Tuple[List[ast.HTMLAttribute], List[token.Token]]:
    # TODO: Correctly parse
    try:
        _,tokens = parse_wildcard(tokens)
        return [[ast.Wildcard()],tokens]
    except ParseError:
        ...

    body, tokens = consume_balanced_token(token.LeftBrace(), token.RightBrace(), tokens)
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

def parse_binary_op(tokens: List[token.Token]) -> Tuple[ast.BinaryFilter, List[token.Token]]:
    if not isinstance(tokens[0], token.Filter):
        raise ParseError(f'Expected filter; got {tokens[0]}')
    
    node_pattern, remainder = parse_node(tokens[1:])
    filter_ast = ast.BinaryFilter(filter_type=tokens[0].filterType, right_arg=node_pattern)

    return (filter_ast, remainder)
    
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

def parse_unpack_operator(tokens: List[token.Token]) -> Tuple[ast.UnpackNode, List[token.Token]]:
    token_types = [ type(t) for t in tokens ]
    match token_types:
        case [token.UnpackOperator, token.Variable, *_]:
            return [ast.UnpackNode(variable=ast.HTMLNode(tag=tokens[1].name, attrs=[], children=[])), tokens[2:]]
    
    raise ParseError(f'Failed to parse unpack operator: {tokens}')
