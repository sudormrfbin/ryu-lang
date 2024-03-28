from typing import Any

from compiler.env import RuntimeEnvironment, TypeEnvironment

from compiler import errors
from compiler.parser import parse, parse_tree_to_ast


def run(source: str, type_env: TypeEnvironment, runtime_env: RuntimeEnvironment) -> Any:
    try:
        return _run(source, type_env, runtime_env)
    except errors.CompilerError as err:
        err.report(source)


def _run(
    source: str, type_env: TypeEnvironment, runtime_env: RuntimeEnvironment
) -> Any:
    tree = parse(source)
    ast = parse_tree_to_ast(tree)

    ast.typecheck(type_env)

    return ast.eval(runtime_env)
