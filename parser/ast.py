from typing import List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import StrEnum

class ASTNodeType(StrEnum):
    STRING = 'string'
    ELLIPSIS = 'ellipsis'
    SET = 'set'
    NODE = 'node'
    UNIFICATION = 'unification'
    WILDCARD = 'wildcard'
    FILTER = 'filter'
    UNPACK = 'unpack'
    VAR_INDEX = 'var_index'

@dataclass
class VariableIndex:
    var: str
    index: str
    nodeType: str = ASTNodeType.VAR_INDEX.value

@dataclass
class Wildcard:
    nodeType: str = ASTNodeType.WILDCARD.value

@dataclass
class String:
    value: str
    nodeType: str = ASTNodeType.STRING.value

@dataclass
class Ellipsis:
    nodeType: str = ASTNodeType.ELLIPSIS.value

@dataclass
class Set:
    members: List[Union[String, Ellipsis]]
    nodeType: str = ASTNodeType.SET.value

@dataclass
class Dict:
    # TODO: Support wildcard values (& perhaps key wildcard as well)
    members: List[Union[Ellipsis, Tuple[String, Union[String,Set]]]]

@dataclass
class HTMLAttribute:
    ...

@dataclass
class HTMLNode:
    tag: Optional[str]
    attrs: List[HTMLAttribute]
    children: List['HTMLNode']
    nodeType: str = ASTNodeType.NODE.value

    @property
    def variable(self) -> bool:
        assert (self.tag is None) or len(self.tag) > 0
        return self.tag and self.tag[0].isupper()

@dataclass
class NodeUnification:
    left: HTMLNode
    right: HTMLNode
    nodeType = ASTNodeType.UNIFICATION.value

@dataclass
class BinaryFilter:
    # NB. Left arg is implicit; the document tree is passed to it
    filter_type: str
    right_arg: HTMLNode
    nodeType = ASTNodeType.FILTER.value

@dataclass
class UnpackNode:
    # TODO: Consider implementing a separate AST node for variables (with associated lookup info)
    variable: HTMLNode
    nodeType = ASTNodeType.UNPACK.value