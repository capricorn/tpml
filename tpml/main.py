import argparse

from bs4 import BeautifulSoup

import parser.parse as parse
import lexer.lex as lex
import runtime.matcher as matcher
from runtime.js import emitter

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tpml_program')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--html', type=str)
    group.add_argument('--bookmarklet', action='store_true', help='Generate a bookmarklet.')
    group.add_argument('--js', action='store_true', help='Generate bundled Javascript.')

    args = parser.parse_args()

    if args.html:
        uni = parse.parse_unification(lex.lex(args.tpml_program))
        with open(args.html, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        print(matcher.unify_tree(uni, root=soup, soup=soup).prettify())
    elif args.bookmarklet:
        print(emitter.emit(args.tpml_program), end='')
    elif args.js:
        print(emitter.emit(args.tpml_program, prefix=False), end='')
    else:
        parser.print_help()