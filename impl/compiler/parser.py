from typing import Any
from lark import Lark, Token, Tree, ast_utils, Transformer

from compiler import ast


GRAMMAR_FILE = "g.lark"
_parser = Lark.open(  # type: ignore
    GRAMMAR_FILE,
    parser="lalr",
    propagate_positions=True,
    rel_to=__file__,
)


def parse(source: str) -> Tree[Token]:
    return _parser.parse(source)


class LarkTreeToAstTransformer(Transformer[Token, Any]):
    def TRUE(self, _) -> bool:
        return True

    def FALSE(self, _) -> bool:
        return False

    def INT(self, n: str) -> int:
        return int(n)

    def STRING(self, s: str) -> str:
        return s[1:-1]  # remove quotes


_transformer: Transformer[
    Token, ast._Ast  # pyright: ignore [reportPrivateUsage]
] = ast_utils.create_transformer(ast, LarkTreeToAstTransformer())  # pyright: ignore [reportUnknownMemberType]


def parse_tree_to_ast(tree: Tree[Token]) -> ast._Ast:  # pyright: ignore [reportPrivateUsage]
    return _transformer.transform(tree)
