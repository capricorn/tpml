from typing import List

from bs4 import BeautifulSoup, Tag

import parser.ast as ast

def match_bs4(program: ast.HTMLNode, soup: BeautifulSoup) -> List[Tag]:
    matches = []
    for node in soup.descendants:
        if isinstance(node, Tag) and node.name == program.tag:
            matches.append(node)
    
    return matches