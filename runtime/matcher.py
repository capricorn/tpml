from typing import List, Optional, Dict

from bs4 import BeautifulSoup, Tag

import parser.ast as ast
from lexer.token import Wildcard

class UnifyException(Exception):
    ...

def match_bs4(program: ast.HTMLNode, soup: BeautifulSoup) -> List[Tag]:
    matches = []
    for node in soup.descendants:
        if isinstance(node, Tag) and node.name == program.tag:
            matches.append(node)
    
    return matches

# Variables is a str/value dictionary (TODO; some sort of sum type for this)
# TODO: Enumerate possibities to account for semantics (enums your friend here..?)
def build_tag(variables, replacement_node: ast.HTMLNode, soup: BeautifulSoup) -> Tag:
    tag = replacement_node.tag
    # If the right tag is a variable, set it to the variable's value
    if replacement_node.variable:
        tag = variables[tag]
        if tag is None:
            raise UnifyException(f'Variable {tag} definition missing.')
    
    new_tag = soup.new_tag(tag)
    # TODO: Attributes (empty for now)
    #new_tag.insert([])
    child_tags = [ build_tag(variables, replacement_node=child, soup=soup) for child in replacement_node.children ]
    new_tag.extend(child_tags)

    return new_tag

def extract_variables(match_rule: ast.HTMLNode, matched_node: Tag) -> Dict:
    vars = dict()
    # TODO: Handle multiple occurrences
    if match_rule.variable:
        vars[match_rule.tag] = matched_node.name
    
    matched_node_children = [ child for child in matched_node.children if isinstance(child, Tag) ]
    # TODO: Handle attributes
    # TODO: Sanity checks?
    for child_rule, child_node in zip(match_rule.children, matched_node_children):
        vars = { **vars, **extract_variables(child_rule, child_node) }

    return vars

def unify(unification: ast.NodeUnification, node: Tag, soup: BeautifulSoup) -> Optional[Tag]:
    ''' If the left unification node matches node, replace node with the right unification node. '''

    # A left side match occurs with the node.
    if unification.left.tag == node.name or unification.left.tag == Wildcard.name:
        if unification.right.tag is None:
            node.decompose()
            return None
        else:
            new_tag = soup.new_tag(unification.right.tag)
            new_tag.extend(list(node.children))
            return new_tag
    else:
        # No left side match so return the node unmodified.
        return node

def unify_tree(unification: ast.NodeUnification, root: Tag, soup: BeautifulSoup) -> Tag:
    #root = root.replace_with(unify(unification, root, soup=soup))
    children = [ e for e in root.children if isinstance(e, Tag) ]

    while children != []:
        child = children.pop(0)
        new_child = unify(unification, child, soup=soup)
        if new_child is None:
            continue
        if child != new_child:
            child.replace_with(new_child)
        children.extend([ e for e in new_child.children if isinstance(e, Tag) ])
    
    return root