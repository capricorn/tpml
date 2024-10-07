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

@dataclass
class NodeUnification:
    left: HTMLNode
    right: HTMLNode