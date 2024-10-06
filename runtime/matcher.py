from typing import List

from bs4 import BeautifulSoup, Tag

import parser.ast as ast

def match_bs4(program: ast.HTMLNode, soup: BeautifulSoup) -> List[Tag]:
    matches = []
    for node in soup.descendants:
        if isinstance(node, Tag) and node.name == program.tag:
            matches.append(node)
    
    return matches

def unify(unification: ast.NodeUnification, node: Tag, soup: BeautifulSoup) -> Tag:
    ''' If the left unification node matches node, replace node with the right unification node. '''

    if unification.left.tag == node.name:
        new_tag = soup.new_tag(unification.right.tag)
        new_tag.extend(node.children)
        return new_tag
    else:
        return node