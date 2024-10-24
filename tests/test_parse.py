from parser import ast
from parser import parse
from lexer import lex

def test_parse_node():
    assert parse.parse('(p,[],[])') == ast.HTMLNode(tag='p', attrs=[], children=[])

def test_parse_unification():
    tokens = lex.lex('(p,[],[]) = (span,[],[])')
    uni = parse.parse_unification(tokens)
    assert uni == ast.NodeUnification(
        left=ast.HTMLNode(tag='p', attrs=[], children=[]),
        right=ast.HTMLNode(tag='span', attrs=[], children=[]))

def test_parse_empty_node():
    assert parse.parse('()') == ast.HTMLNode(tag=None, attrs=[], children=[])

def test_parse_nested_nodes():
    assert parse.parse('(p,[],[(div,[],[])])') == ast.HTMLNode(
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
    tokens = lex.lex('(p,[],[]) = (p,[],[(span,[],[])])')
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
    node = parse.parse('(b,[],_)')
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