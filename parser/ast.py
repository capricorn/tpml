from typing import List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import StrEnum

class ASTNodeType(StrEnum):
    STRING = 'string'
    ELLIPSIS = 'ellipsis'
    SET = 'set'
    NODE = 'node'
    UNIFICATION = 'unification'

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