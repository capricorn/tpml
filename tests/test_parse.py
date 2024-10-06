from parser import ast
from parser import parse

def test_parse_node():
    assert parse.parse('(p,[],[])') == ast.HTMLNode(tag='p', attrs=[], children=[])