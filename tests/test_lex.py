import pytest

from lexer.lex import lex
import lexer.token as token

def test_lex_parens():
    input = '(  )'
    assert lex(input) == [ token.LeftParen(), token.RightParen() ]

def test_lex_wildcard():
    input = '_'
    assert lex(input) == [ token.Wildcard() ]

def test_lex_tag_name():
    input = '(abc)'
    assert lex(input) == [ token.LeftParen(), token.TagName(name='abc'), token.RightParen() ]

def test_lex_comma():
    input = ','
    assert lex(input) == [ token.CommaDelimiter() ] 

def test_lex_bracket():
    input = '[]'
    assert lex(input) == [ token.LeftBracket(), token.RightBracket() ]