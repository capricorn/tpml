import pytest

from bs4 import BeautifulSoup
from bs4 import Tag

import parser.parse as parse
import lexer.lex as lex
from runtime import matcher

def test_bs4_matches():
    with open('tests/data/ask-hn-oct-24.html') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    program = parse.parse('(a,{},[])')
    matches = matcher.match_bs4(program, soup=soup)
    assert matches[0]['href'] == 'https://news.ycombinator.com'

def test_unify_operator():
    soup = BeautifulSoup('', 'html.parser')
    div = soup.new_tag('div')
    span = soup.new_tag('span')

    unification = parse.parse_unification(lex.lex('(div,{},[]) = (p,{},[])'))
    unified_div, div_remainder = matcher.unify(unification, div, soup=soup)
    unified_span, span_remainder = matcher.unify(unification, span, soup=soup)

    assert unified_div.name == 'p' and div_remainder == []
    assert unified_span.name == 'span' and span_remainder == []

@pytest.mark.skip()
def test_unify_tree_identity():
    with open('tests/data/simple.html') as f:
        html = f.read()
        soup = BeautifulSoup(html, 'html.parser')

    unification = parse.parse_unification(lex.lex('(div,[],[]) = (div,[],[])'))
    new_soup = matcher.unify_tree(unification, root=soup, soup=soup)

    soup2 = BeautifulSoup(html, 'html.parser')
    assert soup2 == new_soup

@pytest.mark.skip()
def test_unify_tree_wildcard():
    with open('tests/data/simple.html') as f:
        html = f.read()
        soup = BeautifulSoup(html, 'html.parser')

    unification = parse.parse_unification(lex.lex('(_,[],[]) = (p,[],[])'))
    new_soup = matcher.unify_tree(unification, root=soup, soup=soup)

    transformed_html = '''
    <p>
        <p>
            <p>foo</p>
            <p>bar</p>
            <p>
                <p>baz</p>
            </p>
        </p>
    </p>
    '''
    soup2 = BeautifulSoup(transformed_html, 'html.parser')

    assert soup2.prettify() == new_soup.prettify()

def test_unify_delete_node():
    with open('tests/data/simple.html') as f:
        html = f.read()
        soup = BeautifulSoup(html, 'html.parser')

    unification = parse.parse_unification(lex.lex('(p,{},[]) = ()'))
    new_soup = matcher.unify_tree(unification, root=soup, soup=soup)

    transformed_html = '''
    <html>
        <body>
            <div>
            </div>
        </body>
    </html>
    '''

    soup2 = BeautifulSoup(transformed_html, 'html.parser')
    assert soup2.prettify() == new_soup.prettify()

def test_build_tag():
    rewrite_rule = parse.parse('(p,{},[(X,{},[]),(X,{},[])])')
    soup = BeautifulSoup('', 'html.parser')

    print(rewrite_rule)

    document = '''
    <p>
        <span></span>
        <span></span>
    </p>
    '''

    doc_soup = BeautifulSoup(document, 'html.parser')

    new_tag,_ = matcher.build_tag(variables={'X':'span'}, replacement_node=rewrite_rule, soup=soup)
    assert new_tag.prettify() == doc_soup.prettify()

def test_extract_variables():
    match_rule = parse.parse('(p,{},[(X,{},[]),(Y,{},[])])')

    document = '''
    <p>
        <span></span>
        <div></div>
    </p>
    '''

    soup = BeautifulSoup(document, 'html.parser')
    vars = matcher.extract_variables(match_rule=match_rule, matched_node=soup.p)

    assert ('X' in vars) and (vars['X'] == 'span')
    assert ('Y' in vars) and (vars['Y'] == 'div')

def test_extract_children_variable():
    match_rule = parse.parse('(p,{},Children)')

    document = '''
    <p>
        <span></span>
        <div></div>
    </p>
    '''

    soup = BeautifulSoup(document, 'html.parser')
    vars = matcher.extract_variables(match_rule=match_rule, matched_node=soup.p)

    assert 'Children' in vars and [ c for c in soup.p.children if isinstance(c, Tag) ] == vars['Children']

def test_bold_spans():
    match_rule = parse.parse_unification(lex.lex('(span,{},Children) = (b,{},[(span,{},Children)])'))

    document = '''
    <p>
        <span></span>
        <div></div>
    </p>
    '''

    new_doc = '''
    <p>
        <b><span></span></b>
        <div></div>
    </p>
    '''

    soup = BeautifulSoup(document, 'html.parser')
    new_tree = matcher.unify_tree(unification=match_rule, root=soup.p, soup=soup)
    #new_tree = matcher.unify(unification=match_rule, node=soup.p, soup=soup)
    new_soup = BeautifulSoup(new_doc, 'html.parser')


    assert new_tree.prettify() == new_soup.prettify()
    #vars = matcher.extract_variables(match_rule=match_rule, matched_node=soup.p)