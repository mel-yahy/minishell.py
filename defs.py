from dataclasses import dataclass
from enum import Enum


class RedirType(Enum):
    INPUT = 0
    OUTPUT = 1
    APPEND = 2
    HEREDOC = 3
    DEFAULT = 4


class AstType(Enum):
    PIPELINE = 0
    CMD = 1


@dataclass
class RedirNode:
    type: RedirType
    target: str
    src_fd: int
    next: "RedirNode | None" = None

    def append_back(self, new_node: "RedirNode") -> None:
        curr = self
        while curr.next:
            curr = curr.next
        curr.next = new_node


@dataclass
class CmdNode:
    name: str
    path: str | None
    args: list[str]
    redir: RedirNode | None = None


@dataclass
class AstNode:
    type: AstType
    right: "AstNode | None" = None
    left: "AstNode | None" = None
    cmd: CmdNode | None = None


class ParseError(Exception):
    pass
