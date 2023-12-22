from lark import Lark, Tree, ast_utils, Transformer

from . import ast

GRAMMAR_FILE = "g.lark"
_parser = Lark.open(
    GRAMMAR_FILE,
    parser="lalr",
    propagate_positions=True,
    rel_to=__file__,
)


def parse(source: str) -> Tree:
    return _parser.parse(source)


class LarkTreeToAstTransformer(Transformer):
    def TRUE(self, _):
        return True

    def FALSE(self, _):
        return False

    def INT(self, n):
        return int(n)


_transformer = ast_utils.create_transformer(ast, LarkTreeToAstTransformer())


def parse_tree_to_ast(tree: Tree) -> ast._Ast:
    return _transformer.transform(tree)
