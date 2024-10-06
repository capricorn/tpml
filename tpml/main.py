import argparse

from bs4 import BeautifulSoup

import parser.parse as parse
import lexer.lex as lex
import runtime.matcher as matcher

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tpml_program')
    parser.add_argument('--html', type=str, required=True)

    args = parser.parse_args()

    uni = parse.parse_unification(lex.lex(args.tpml_program))
    with open(args.html, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    print(matcher.unify_tree(uni, root=soup, soup=soup).prettify())