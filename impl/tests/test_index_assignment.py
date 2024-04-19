from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.langtypes import INT, Array
from tests.utils import docstring_source_with_snapshot


@docstring_source_with_snapshot
def test_index_assignment(source: str, snapshot: Any):
    """
    let x = [2,3]
    x[1]=4
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get_var_type("x") == Array(INT)

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == [2, 4]
