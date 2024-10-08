from typing import List, Optional
from dataclasses import dataclass

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