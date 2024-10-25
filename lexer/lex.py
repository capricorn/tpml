from typing import List, Tuple
from dataclasses import dataclass
import re

import lexer.token as token

class LexError(Exception):
    ...

@dataclass
class LexResult():
    remaining_input: str
    token: token.Token

def colon(input: str) -> bool:
    return input[:1] == ':'

def ellipsis(input: str) -> bool:
    return input[:3] == '...'

def brace(input: str) -> bool:
    match list(input):
        case [ '{', *_ ]:
            return True
        case [ '}', *_ ]:
            return True
    
    return False

def string(input: str) -> bool:
    assert len(input) > 0
    return input[0] == '"'

def tag(input: str) -> bool:
    return (re.match('[a-z]', input) is not None)

def bracket(input: str) -> bool:
    assert len(input) > 0
    return input[0] == '[' or input[0] == ']'

def unification(input: str) -> bool:
    assert len(input) > 0
    return input[0] == '='

def variable(input: str) -> bool:
    assert len(input) > 0
    return (re.match('[A-Z]', input) is not None)

def consume_colon(input: str) -> Tuple[str, token.Token]:
    assert len(input) >= 1
    return (input[1:], token.Colon())

def consume_ellipsis(input: str) -> Tuple[str, token.Token]:
    assert len(input) >= 3
    return (input[3:], token.Ellipsis())

def consume_brace(input: str) -> Tuple[str, token.Token]:
    match list(input):
        case [ '{', *_ ]:
            return (input[1:], token.LeftBrace())
        case [ '}', *_ ]:
            return (input[1:], token.RightBrace())
    
    raise LexError()

def consume_string(input: str) -> Tuple[str, token.Token]:
    # 'input' must at least be an empty string
    assert len(input) >= 2
    # TODO: Handle escaped quotes 
    match = re.match(r'"(.*?)"', input)
    if match is None:
        raise LexError()
    
    remainder = input[match.end(0):]
    string = token.String(value=match.group(0)[1:-1])

    return (remainder, string)

def consume_unification(input: str) -> Tuple[str, token.Token]:
    assert len(input) > 0
    assert input[0] == '='

    return (input[1:], token.Unification())

def consume_paren(input: str) -> Tuple[str, token.Token]:
    assert len(input) > 0
    ch = input[0]

    if ch == '(':
        return (input[1:], token.LeftParen())
    elif ch == ')':
        return (input[1:], token.RightParen())
    else:
        assert False, "'ch' is not a parenthesis."

def consume_wildcard(input: str) -> Tuple[str, token.Token]:
    assert len(input) > 0
    assert input[0] == '_'

    return (input[1:], token.Wildcard())

def consume_tag(input: str) -> Tuple[str, token.Token]:
    assert len(input) > 0

    idx = 0
    while tag(input[idx:]):
        idx += 1
    
    tag_str = input[:idx]
    assert tag_str != ''

    return (input[idx:], token.TagName(name=tag_str))

def consume_variable(input: str) -> Tuple[str, token.Token]:
    assert len(input) > 0

    remainder, tag = consume_tag(input[0].lower() + input[1:])
    var = token.Variable(name=tag.name.title())

    return remainder, var

def consume_comma(input: str) -> Tuple[str, token.Token]:
    assert len(input) > 0
    assert input[0] == ','

    return (input[1:], token.CommaDelimiter())

def consume_bracket(input: str) -> Tuple[str, token.Token]:
    assert len(input) > 0
    ch = input[0]

    if ch == '[':
        return (input[1:], token.LeftBracket())
    elif ch == ']':
        return (input[1:], token.RightBracket())
    else:
        assert False, "'ch' is not a bracket."

def lex(input: str) -> List[token.Token]:
    tokens = []
    while input != '':
        token = None
        ch = input[0]

        if ch == '(' or ch == ')':
            input, token = consume_paren(input)
        elif ch == ' ':
            input = input[1:]
        elif ch == '_':
            input, token = consume_wildcard(input)
        elif ch == ',':
            input, token = consume_comma(input)
        elif tag(input):
            input, token = consume_tag(input)
        elif bracket(input):
            input, token = consume_bracket(input)
        elif unification(input):
            input, token = consume_unification(input)
        elif variable(input):
            input, token = consume_variable(input)
        elif string(input):
            input, token = consume_string(input)
        elif brace(input):
            input, token = consume_brace(input)
        elif ellipsis(input):
            input, token = consume_ellipsis(input)
        elif colon(input):
            input, token = consume_colon(input)
        else:
            raise LexError()
        
        if token:
            tokens.append(token)

    return tokens