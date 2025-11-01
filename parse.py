from defs import RedirNode, CmdNode, AstNode, AstType, RedirType
from utils import isRedirToken, getRedirType, findCmdPath


def getSrcFd(type: RedirType) -> int:
    if type in (RedirType.INPUT, RedirType.HEREDOC):
        return 0
    else:
        return 1


def parseRedir(tokens: list[str]) -> RedirNode | None:
    redir: RedirNode | None = None
    i = 0
    while i < len(tokens):
        if isRedirToken(tokens[i]):
            newNode = RedirNode(
                type=getRedirType(tokens[i]),
                target=tokens[i + 1],
                src_fd=getSrcFd(getRedirType(tokens[i])),
            )
            if redir is None:
                redir = newNode
            else:
                redir.appendBack(newNode)
            i += 2
        else:
            i += 1
    return redir


def parseCmd(tokens: list[str]) -> CmdNode | None:
    cmdTokens: list[str] = []
    i = 0
    while i < len(tokens) and tokens[i]:
        if isRedirToken(tokens[i]):
            i += 2
        else:
            cmdTokens.append(tokens[i])
            i += 1
    cmdNode = CmdNode(name=cmdTokens[0], args=cmdTokens, path=findCmdPath(cmdTokens[0]))
    cmdNode.redir = parseRedir(tokens)
    return cmdNode


def parsePipeline(tokens: list[str]) -> AstNode | None:
    try:
        pipe = tokens.index("|")
    except ValueError:
        return AstNode(type=AstType.CMD, right=None, left=None, cmd=parseCmd(tokens))
    leftTokens = tokens[:pipe]
    rightTokens = tokens[pipe + 1 :]
    astNode = AstNode(type=AstType.PIPELINE)
    astNode.left = AstNode(type=AstType.CMD, cmd=parseCmd(leftTokens))
    astNode.right = parsePipeline(rightTokens)
    return astNode
