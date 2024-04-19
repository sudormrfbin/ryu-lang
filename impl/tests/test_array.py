from typing import Any
from compiler.compiler import get_default_environs
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.langtypes import INT, Array
from tests.utils import docstring_source_with_snapshot


@docstring_source_with_snapshot
def test_array_statement_basic(source: str, snapshot: Any):
    """
    let x = [2,3+3]
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get_var_type("x") == Array(INT)

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == [2, 6]


@docstring_source_with_snapshot
def test_array_with_annotation(source: str, snapshot: Any):
    """
    let x = <int>[1]
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env, env = get_default_environs()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get_var_type("x") == Array(INT)

    ast.eval(env)
    assert env.get("x") == [1]


@docstring_source_with_snapshot
def test_empty_array(source: str, snapshot: Any):
    """
    let x = <int>[]
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env, env = get_default_environs()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get_var_type("x") == Array(INT)

    ast.eval(env)
    assert env.get("x") == []
