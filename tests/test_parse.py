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