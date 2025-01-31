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

def test_lex_unification():
    input = '[] ='
    assert lex(input) == [ token.LeftBracket(), token.RightBracket(), token.Unification() ]

def test_lex_variable():
    input = '(Tag,_,_)'
    assert lex(input) == [
        token.LeftParen(),
        token.Variable(name='Tag'),
        token.CommaDelimiter(),
        token.Wildcard(),
        token.CommaDelimiter(),
        token.Wildcard(),
        token.RightParen()
    ]

def test_lex_string():
    input = '( "foo" )'
    assert lex(input) == [
        token.LeftParen(),
        token.String(value='foo'),
        token.RightParen()
    ]

def test_lex_braces():
    input = '{ "foo" }'
    assert lex(input) == [
        token.LeftBrace(),
        token.String(value='foo'),
        token.RightBrace()
    ]

def test_lex_ellipses():
    input = '{ ... }'
    assert lex(input) == [
        token.LeftBrace(),
        token.Ellipsis(),
        token.RightBrace()
    ]

def test_lex_colon():
    input = '{ "foo": "bar" }'
    assert lex(input) == [
        token.LeftBrace(),
        token.String(value='foo'),
        token.Colon(),
        token.String(value='bar'),
        token.RightBrace()
    ]

def test_lex_any_subtree_filter():
    input = '..>'
    assert lex(input) == [
        token.Filter(filterType=token.Filter.Type.ANY_DEPTH_SUBTREE_MATCH)
    ]

def test_lex_unpack_operator():
    input = '*'
    assert lex(input) == [
        token.UnpackOperator()
    ]