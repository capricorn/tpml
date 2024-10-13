import argparse

from bs4 import BeautifulSoup

import parser.parse as parse
import lexer.lex as lex
import runtime.matcher as matcher

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tpml_program')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--html', type=str)
    group.add_argument('--bookmarklet', action='store_true')

    args = parser.parse_args()

    if args.html:
        uni = parse.parse_unification(lex.lex(args.tpml_program))
        with open(args.html, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        print(matcher.unify_tree(uni, root=soup, soup=soup).prettify())
    elif args.bookmarklet:
        ...
    else:
        parser.print_help()