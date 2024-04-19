from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.langtypes import BOOL, INT
from compiler.parser import parse, parse_tree_to_ast


def test_variable_delcaration(snapshot: Any):
    ast = parse_tree_to_ast(parse("let x = 1"))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot
    assert type_env.get_var_type("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 1


def test_variable_delcaration_with_expressions(snapshot: Any):
    ast = parse_tree_to_ast(parse("let variable = 3 * 4 == 10"))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot
    assert type_env.get_var_type("variable") == BOOL

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("variable") is False
