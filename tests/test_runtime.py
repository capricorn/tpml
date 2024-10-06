from bs4 import BeautifulSoup

import parser.parse as parse
from runtime import matcher

def test_bs4_matches():
    with open('tests/data/ask-hn-oct-24.html') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    program = parse.parse('(a,[],[])')
    matches = matcher.match_bs4(program, soup=soup)
    assert matches[0]['href'] == 'https://news.ycombinator.com'
