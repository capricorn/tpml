from typing import List

from bs4 import BeautifulSoup, Tag

import parser.ast as ast
from lexer.token import Wildcard

def match_bs4(program: ast.HTMLNode, soup: BeautifulSoup) -> List[Tag]:
    matches = []
    for node in soup.descendants:
        if isinstance(node, Tag) and node.name == program.tag:
            matches.append(node)
    
    return matches

def unify(unification: ast.NodeUnification, node: Tag, soup: BeautifulSoup) -> Tag:
    ''' If the left unification node matches node, replace node with the right unification node. '''

    if unification.left.tag == node.name or unification.left.tag == Wildcard.name:
        new_tag = soup.new_tag(unification.right.tag)
        new_tag.extend(list(node.children))
        return new_tag
    else:
        return node

def unify_tree(unification: ast.NodeUnification, root: Tag, soup: BeautifulSoup) -> Tag:
    #root = root.replace_with(unify(unification, root, soup=soup))
    children = [ e for e in root.children if isinstance(e, Tag) ]

    while children != []:
        child = children.pop(0)
        new_child = unify(unification, child, soup=soup)
        if child != new_child:
            child.replace_with(new_child)
        children.extend([ e for e in new_child.children if isinstance(e, Tag) ])
    
    return root