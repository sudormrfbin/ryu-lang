from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from tests.utils import docstring_source_with_snapshot


@docstring_source_with_snapshot
def test_print(source: str, snapshot: Any):
    """
    print("hello world")
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    env = RuntimeEnvironment()
    ast.eval(env)


# test2
@docstring_source_with_snapshot
def test_print_variable(source: str, snapshot: Any):
    """
    let x=2
    print(x+1)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot
    env = RuntimeEnvironment()
    ast.eval(env)
