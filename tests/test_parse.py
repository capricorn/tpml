import pytest

from parser import ast
from parser import parse
from lexer import lex

def test_parse_node():
    assert parse.parse('(p,{},[])') == ast.HTMLNode(tag='p', attrs=[], children=[])

def test_parse_unification():
    tokens = lex.lex('(p,{},[]) = (span,{},[])')
    uni = parse.parse_unification(tokens)
    assert uni == ast.NodeUnification(
        left=ast.HTMLNode(tag='p', attrs=[], children=[]),
        right=ast.HTMLNode(tag='span', attrs=[], children=[]))

def test_parse_empty_node():
    assert parse.parse('()') == ast.HTMLNode(tag=None, attrs=[], children=[])

def test_parse_nested_nodes():
    assert parse.parse('(p,{},[(div,{},[])])') == ast.HTMLNode(
        tag='p',
        attrs=[],
        children=[
            ast.HTMLNode(
                tag='div',
                attrs=[],
                children=[]
            )
        ])

def test_parse_nested_unification():
    tokens = lex.lex('(p,{},[]) = (p,{},[(span,{},[])])')
    uni = parse.parse_unification(tokens)

    assert uni == ast.NodeUnification(
        left=ast.HTMLNode(
            tag='p',
            attrs=[],
            children=[]
        ),
        right=ast.HTMLNode(
            tag='p',
            attrs=[],
            children=[
                ast.HTMLNode(
                    tag='span',
                    attrs=[],
                    children=[]
                )
            ]
        )
    )

def test_parse_wildcard_child():
    node = parse.parse('(b,{},_)')
    assert node == ast.HTMLNode(
        tag='b',
        attrs=[],
        children=[
            ast.HTMLNode(
                tag='_',
                attrs=[],
                children=[]
            )
        ]
    )

def test_parse_ellipsis():
    tokens = lex.lex('...')
    ellipsis, tokens = parse.parse_ellipsis(tokens)

    assert tokens == []
    assert isinstance(ellipsis, ast.Ellipsis)

def test_parse_string():
    tokens = lex.lex('"foo"')
    string, tokens = parse.parse_string(tokens)

    assert tokens == []
    assert string.value == 'foo'

def test_parse_set_multiple():
    tokens = lex.lex('{ "foo", "bar" }')
    ast_set, tokens = parse.parse_set(tokens)

    assert tokens == []
    assert ast_set == ast.Set(
        members=[
            ast.String(value='foo'),
            ast.String(value='bar')
        ])

def test_parse_set_single():
    tokens = lex.lex('{ "foo" }')
    ast_set, tokens = parse.parse_set(tokens)

    assert tokens == []
    assert ast_set == ast.Set(members=[ast.String(value='foo')])

def test_parse_set_empty():
    tokens = lex.lex('{}')
    ast_set, tokens = parse.parse_set(tokens)

    assert tokens == []
    assert ast_set == ast.Set(members=[])

def test_parse_set_ellipsis_single():
    tokens = lex.lex('{ ... }')
    ast_set, tokens = parse.parse_set(tokens)

    assert tokens == []
    assert ast_set == ast.Set(members=[ast.Ellipsis()])

def test_parse_set_ellipsis_multiple():
    tokens = lex.lex('{ ..., "foo", "bar" }')
    ast_set, tokens = parse.parse_set(tokens)

    assert tokens == []
    assert ast_set == ast.Set(members=[
        ast.Ellipsis(),
        ast.String(value='foo'),
        ast.String(value='bar')
    ])

def test_parse_dict_single_strings_only():
    tokens = lex.lex('{ "foo": "bar" }')
    ast_dict, tokens = parse.parse_dict(tokens)

    assert tokens == []
    assert ast_dict == ast.Dict(members=[
        (ast.String(value='foo'), ast.String(value='bar'))
    ])

def test_parse_dict_empty():
    tokens = lex.lex('{}')
    ast_dict, tokens = parse.parse_dict(tokens)

    assert tokens == []
    assert ast_dict == ast.Dict(members=[])

def test_parse_dict_multiple_strings_only():
    tokens = lex.lex('{ "foo": "bar", "baz": "qux" }')
    ast_dict, tokens = parse.parse_dict(tokens)

    assert tokens == []
    assert ast_dict == ast.Dict(members=[
        (ast.String(value='foo'), ast.String(value='bar')),
        (ast.String(value='baz'), ast.String(value='qux')),
    ])

def test_parse_dict_set_value():
    tokens = lex.lex('{ "foo": { "bar", "baz" }, "qux": "fred" }')
    ast_dict, tokens = parse.parse_dict(tokens)

    assert tokens == []
    assert ast_dict == ast.Dict(members=[
        (ast.String(value='foo'), ast.Set(members=[ast.String(value='bar'), ast.String(value='baz')])),
        (ast.String(value='qux'), ast.String(value='fred'))
    ])

def test_parse_dict_trailing_comma_failure():
    tokens = lex.lex('{ "foo": "bar", }')

    try:
        parse.parse_dict(tokens)
    except parse.ParseError:
        return
    
    pytest.fail('Expected ParseError')

def test_parse_dict_wildcard_value():
    tokens = lex.lex('{ "foo": _ }')
    ast_dict, tokens = parse.parse_dict(tokens)

    assert tokens == []
    assert ast_dict == ast.Dict(members=[
        (ast.String(value='foo'), ast.Wildcard())
    ])

def test_parse_fuzzy_dict():
    tokens = lex.lex('{ "foo": "bar", ... }')
    ast_dict, tokens = parse.parse_dict(tokens)

    assert tokens == []
    assert ast_dict == ast.Dict(members=[
        (ast.String(value='foo'), ast.String(value='bar')),
        ast.Ellipsis()
    ])

def test_parse_any_subtree_op():
    tokens = lex.lex('..> (div,{},[])')
    ast_filter, tokens = parse.parse_binary_op(tokens)
    assert tokens == []
    assert ast_filter == ast.BinaryFilter(
        filter_type=lex.token.Filter.Type.ANY_DEPTH_SUBTREE_MATCH,
        right_arg=ast.HTMLNode(
            tag='div',
            attrs=[],
            children=[],
        )
    )

def test_parse_attribute_wildcard():
    tokens = lex.lex('_')
    ast_wildcard, tokens = parse.parse_attributes(tokens)
    assert tokens == []
    assert len(ast_wildcard) == 1
    assert ast_wildcard[0] == ast.Wildcard()

def test_parse_unpack_operator():
    tokens = lex.lex('*Foo')
    ast_unpack, tokens = parse.parse_unpack_operator(tokens)

    assert type(ast_unpack) == ast.UnpackNode
    assert ast_unpack.variable.tag == 'Foo'
    assert ast_unpack.variable.variable
    assert tokens == []

def test_parse_dict_unpack_entry():
    tokens = lex.lex('{"foo":"bar", *Foo, "baz":"bar"}')
    ast_dict, tokens = parse.parse_dict(tokens)

    assert tokens == []
    assert ast_dict.members == [
        (ast.String(value='foo'), ast.String(value='bar')),
        ast.UnpackNode(variable=ast.HTMLNode(tag='Foo', attrs=[], children=[])),
        (ast.String(value='baz'), ast.String(value='bar')),
    ]