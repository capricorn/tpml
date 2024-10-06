from typing import List, Tuple

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
        if tok == left_match:
            stack += 1
        elif tok == right_match:
            stack -= 1
            if stack == 0:
                body = tokens[1:i]
                break
    
    if body is None:
        raise ParseError()
    
    return (body, tokens[i+1:])

def parse_tag(tokens: List[token.Token]) -> Tuple[str, List[token.Token]]:
    if len(tokens) == 0:
        raise ParseError()

    if not isinstance(tokens[0], token.TagName):
        raise ParseError()
    
    return (tokens[0].name, tokens[1:])

def parse_comma_delim(tokens: List[token.Token]) -> List[token.Token]:
    if len(tokens) == 0:
        raise ParseError()
    if not isinstance(tokens[0], token.CommaDelimiter):
        raise ParseError()
    
    return tokens[1:]

def parse_attributes(tokens: List[token.Token]) -> Tuple[List[ast.HTMLAttribute], List[token.Token]]:
    # TODO: Correctly parse
    body, tokens = consume_balanced_token(token.LeftBracket(), token.RightBracket(), tokens)
    return body, tokens

def parse_children(tokens: List[token.Token]) -> Tuple[List[ast.HTMLNode], List[token.Token]]:
    # TODO: Correctly parse
    body, tokens = consume_balanced_token(token.LeftBracket(), token.RightBracket(), tokens)
    return body, tokens

def parse_node(tokens: List[token.Token]) -> ast.HTMLNode:
    body,_ = consume_balanced_token(token.LeftParen(), token.RightParen(), tokens)

    tag, body = parse_tag(body)
    body = parse_comma_delim(body)
    attrs, body = parse_attributes(body)
    body = parse_comma_delim(body)
    children, body = parse_children(body)

    return ast.HTMLNode(tag=tag, attrs=attrs, children=children)

def parse(input: str) -> ast.HTMLNode:
    tokens = lex.lex(input)
    # Initially, _only_ parse nodes of the form (tag,[],[])
    return parse_node(tokens)

