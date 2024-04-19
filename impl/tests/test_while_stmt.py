from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.langtypes import INT
from tests.utils import docstring_source_with_snapshot


@docstring_source_with_snapshot
def test_while_stmt(source: str, snapshot: Any):
    """
    //ignore
    let x = 5
    while x!=0 {
        x = x-1
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot
    assert type_env.get_var_type("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 0
