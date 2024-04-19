from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.langtypes import STRING
from tests.utils import docstring_source_with_snapshot


@docstring_source_with_snapshot
def test_lexical_scope_variable_shadowing(source: str, snapshot: Any):
    """
    let x = "outside"
    if true {
        let x = "inside"
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get_var_type("x") == STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == "outside"


@docstring_source_with_snapshot
def test_lexical_scope_variable_type(source: str, snapshot: Any):
    """
    let x = "outside"
    if true {
        let x = 8
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get_var_type("x") == STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == "outside"
