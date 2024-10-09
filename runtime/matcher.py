from typing import List, Optional, Dict, Tuple

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
def build_tag(variables, replacement_node: ast.HTMLNode, soup: BeautifulSoup) -> Tuple[Tag, List[ast.HTMLNode]]:
    remaining_children = []
    tag = replacement_node.tag
    # If the right tag is a variable, set it to the variable's value
    if replacement_node.variable:
        tag = variables[tag]
        if tag is None:
            raise UnifyException(f'Variable {tag} definition missing.')
    
    # Handle children as a list or var
    new_tag = soup.new_tag(tag)
    # TODO: Attributes (empty for now)
    # Special case where the list is a variable
    # TODO: Infinite loop since the same children are iterated again
    if len(replacement_node.children) == 1 and replacement_node.children[0].variable:
        # TODO: Return future children to iterate here..?
        # (ie recursively extend a list of 'remaining_children', return it.)
        new_tag.extend(variables[replacement_node.children[0].tag])
        remaining_children.extend(variables[replacement_node.children[0].tag])
    else:
        child_tags = [ build_tag(variables, replacement_node=child, soup=soup) for child in replacement_node.children ]
        if child_tags != []:
            new_tag.extend([ child[0] for child in child_tags ])
            for child in child_tags:
                remaining_children.extend(child[1])

    return new_tag, remaining_children

def extract_variables(match_rule: ast.HTMLNode, matched_node: Tag) -> Dict:
    vars = dict()
    # TODO: Handle multiple occurrences
    if match_rule.variable:
        vars[match_rule.tag] = matched_node.name

    if len(match_rule.children) == 1 and match_rule.children[0].variable:
        vars[match_rule.children[0].tag] = [ child for child in matched_node.children if isinstance(child, Tag) ]
        return vars
    
    matched_node_children = [ child for child in matched_node.children if isinstance(child, Tag) ]
    # TODO: Handle attributes
    # TODO: Sanity checks?
    for child_rule, child_node in zip(match_rule.children, matched_node_children):
        vars = { **vars, **extract_variables(child_rule, child_node) }

    return vars

def unify(unification: ast.NodeUnification, node: Tag, soup: BeautifulSoup) -> Tuple[Optional[Tag], List[ast.HTMLNode]]:
    ''' If the left unification node matches node, replace node with the right unification node. '''

    # A left side match occurs with the node.
    if unification.left.tag == node.name or unification.left.tag == Wildcard.name:
        if unification.right.tag is None:
            node.decompose()
            return (None, [])
        else:
            vars = extract_variables(unification.left, node)
            new_tag = build_tag(variables=vars, replacement_node=unification.right, soup=soup)
            return new_tag
    else:
        # No left side match so return the node unmodified.
        return (node, [ e for e in node.children if isinstance(e, Tag) ])

def unify_tree(unification: ast.NodeUnification, root: Tag, soup: BeautifulSoup) -> Tag:
    #root = root.replace_with(unify(unification, root, soup=soup))
    children = [ e for e in root.children if isinstance(e, Tag) ]

    while children != []:
        child = children.pop(0)
        new_child, remainder = unify(unification, child, soup=soup)
        if new_child is None:
            continue
        if child != new_child:
            child.replace_with(new_child)

        children.extend(remainder)
    
    return root