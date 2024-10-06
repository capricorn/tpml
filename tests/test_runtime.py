from bs4 import BeautifulSoup

import parser.parse as parse
import lexer.lex as lex
from runtime import matcher

def test_bs4_matches():
    with open('tests/data/ask-hn-oct-24.html') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    program = parse.parse('(a,[],[])')
    matches = matcher.match_bs4(program, soup=soup)
    assert matches[0]['href'] == 'https://news.ycombinator.com'

def test_unify_operator():
    soup = BeautifulSoup('', 'html.parser')
    div = soup.new_tag('div')
    span = soup.new_tag('span')

    unification = parse.parse_unification(lex.lex('(div,[],[]) = (p,[],[])'))
    unified_div = matcher.unify(unification, div, soup=soup)
    unified_span = matcher.unify(unification, span, soup=soup)

    assert unified_div.name == 'p'
    assert unified_span.name == 'span'

def test_unify_tree_identity():
    with open('tests/data/simple.html') as f:
        html = f.read()
        soup = BeautifulSoup(html, 'html.parser')

    unification = parse.parse_unification(lex.lex('(div,[],[]) = (div,[],[])'))
    new_soup = matcher.unify_tree(unification, root=soup, soup=soup)

    soup2 = BeautifulSoup(html, 'html.parser')
    assert soup2 == new_soup