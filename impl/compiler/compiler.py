from typing import Any

from .parser import parse, parse_tree_to_ast


def run(source: str) -> Any:
    tree = parse(source)
    ast = parse_tree_to_ast(tree)

    ast.typecheck()

    return ast.eval()
