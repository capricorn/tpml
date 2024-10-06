from dataclasses import dataclass

@dataclass
class Token():
    ...

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