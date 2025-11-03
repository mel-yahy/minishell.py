from defs import RedirNode, CmdNode, AstNode, AstType, RedirType
from utils import is_redir_token, get_redir_type, find_cmd_path


def get_src_fd(type: RedirType) -> int:
    if type in (RedirType.INPUT, RedirType.HEREDOC):
        return 0
    else:
        return 1


def parse_redir(tokens: list[str]) -> RedirNode | None:
    redir: RedirNode | None = None
    i = 0
    while i < len(tokens):
        if is_redir_token(tokens[i]):
            new_node = RedirNode(
                type=get_redir_type(tokens[i]),
                target=tokens[i + 1],
                src_fd=get_src_fd(get_redir_type(tokens[i])),
            )
            if redir is None:
                redir = new_node
            else:
                redir.append_back(new_node)
            i += 2
        else:
            i += 1
    return redir


def parse_cmd(tokens: list[str]) -> CmdNode | None:
    cmd_tokens: list[str] = []
    i = 0
    while i < len(tokens) and tokens[i]:
        if is_redir_token(tokens[i]):
            i += 2
        else:
            cmd_tokens.append(tokens[i])
            i += 1
    cmd_node = CmdNode(
        name=cmd_tokens[0], args=cmd_tokens, path=find_cmd_path(cmd_tokens[0])
    )
    cmd_node.redir = parse_redir(tokens)
    return cmd_node


def parse_pipeline(tokens: list[str]) -> AstNode | None:
    try:
        pipe = tokens.index("|")
    except ValueError:
        return AstNode(type=AstType.CMD, right=None, left=None, cmd=parse_cmd(tokens))
    left_tokens = tokens[:pipe]
    right_tokens = tokens[pipe + 1 :]
    ast_node = AstNode(type=AstType.PIPELINE)
    ast_node.left = AstNode(type=AstType.CMD, cmd=parse_cmd(left_tokens))
    ast_node.right = parse_pipeline(right_tokens)
    return ast_node
