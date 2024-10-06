from typing import List
from dataclasses import dataclass

@dataclass
class HTMLAttribute:
    ...

@dataclass
class HTMLNode:
    tag: str
    attrs: List[HTMLAttribute]
    children: List['HTMLNode']

@dataclass
class NodeUnification:
    left: HTMLNode
    right: HTMLNode