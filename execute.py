import sys
from defs import AstNode, AstType, CmdNode, RedirNode, RedirType
from utils import expandEnvVars
import os


def handleHereDoc(redir: RedirNode) -> int:
    readEnd, writeEnd = os.pipe()
    while True:
        try:
            line = input()
        except EOFError:
            print(
                f"\nwarning: here-document delimited by end-of-file (wanted '{redir.target}')",
                file=sys.stderr,
            )
            break
        if line == redir.target:
            break
        line += "\n"
        _ = os.write(writeEnd, line.encode())
    os.close(writeEnd)
    return readEnd


def setupRedirs(redir: RedirNode) -> None:
    if redir.type is RedirType.HEREDOC:
        fd = handleHereDoc(redir)
    elif redir.type is RedirType.INPUT:
        fd = os.open(redir.target, os.O_RDONLY)
    elif redir.type is RedirType.OUTPUT:
        fd = os.open(redir.target, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o644)
    elif redir.type is RedirType.APPEND:
        fd = os.open(redir.target, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o644)
    else:
        raise ValueError("It will never reach here... Maybe")
    _ = os.dup2(fd, redir.src_fd)
    os.close(fd)


def executeCmd(cmd: CmdNode) -> None:
    if cmd.redir:
        setupRedirs(cmd.redir)
    if not cmd.path:
        print(f"{cmd.name}: command was not found", file=sys.stderr)
        sys.exit(127)
    expandEnvVars(cmd.args)
    os.execve(cmd.path, cmd.args, os.environ)


def executePipeline(ast: AstNode) -> int:
    readEnd, writeEnd = os.pipe()
    id_1 = os.fork()
    if id_1 == 0:
        os.close(readEnd)
        if ast.left and ast.left.cmd:
            _ = os.dup2(writeEnd, 1)
            os.close(writeEnd)
            executeCmd(ast.left.cmd)
        sys.exit(1)
    id_2 = os.fork()
    if id_2 == 0:
        os.close(writeEnd)
        if ast.right:
            _ = os.dup2(readEnd, 0)
            os.close(readEnd)
            execute(ast.right)
        sys.exit(1)
    os.close(readEnd)
    os.close(writeEnd)
    _ = os.waitpid(id_1, 0)
    _, status = os.waitpid(id_2, 0)
    if os.WIFEXITED(status):
        return status
    else:
        return 1


def execute(ast: AstNode) -> None:
    lastExitStatus = 0
    if ast.type is AstType.PIPELINE:
        lastExitStatus = executePipeline(ast)
    elif ast.type is AstType.CMD and ast.cmd:
        id = os.fork()
        if id == 0:
            executeCmd(ast.cmd)
        _, status = os.waitpid(id, 0)
        if os.WIFEXITED(status):
            lastExitStatus = status
        else:
            lastExitStatus = 1
