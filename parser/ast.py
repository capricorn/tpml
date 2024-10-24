from typing import List, Optional, Union
from dataclasses import dataclass

@dataclass
class String:
    value: str

@dataclass
class Ellipsis:
    ...

@dataclass
class Set:
    members: List[Union[String, Ellipsis]]

@dataclass
class HTMLAttribute:
    ...

@dataclass
class HTMLNode:
    tag: Optional[str]
    attrs: List[HTMLAttribute]
    children: List['HTMLNode']

    @property
    def variable(self) -> bool:
        assert (self.tag is None) or len(self.tag) > 0
        return self.tag and self.tag[0].isupper()

@dataclass
class NodeUnification:
    left: HTMLNode
    right: HTMLNode