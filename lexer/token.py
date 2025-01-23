from dataclasses import dataclass
from enum import StrEnum

@dataclass
class Token():
    ...

@dataclass
class Colon(Token):
    ...

@dataclass
class Ellipsis(Token):
    ...

@dataclass
class String(Token):
    value: str

@dataclass
class LeftParen(Token):
    ...

@dataclass
class RightParen(Token):
    ...

@dataclass
class CommaDelimiter(Token):
    ...

@dataclass
class TagName(Token):
    name: str

@dataclass
class Wildcard(Token):
    name = '_'

@dataclass
class LeftBrace(Token):
    ...

@dataclass
class RightBrace(Token):
    ...

@dataclass
class LeftBracket(Token):
    ...

@dataclass
class RightBracket(Token):
    ...

@dataclass
class Unification(Token):
    ...

@dataclass
class Variable(Token):
    name: str

@dataclass
class UnpackOperator(Token):
    ''' The prefix operator "*Variable" '''
    ...

@dataclass
class Filter(Token):
    class Type(StrEnum):
        ANY_DEPTH_SUBTREE_MATCH = '..>'

    filterType: str