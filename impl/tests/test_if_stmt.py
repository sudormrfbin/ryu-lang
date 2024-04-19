from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.langtypes import INT, STRING
from tests.utils import docstring_source_with_snapshot


@docstring_source_with_snapshot
def test_if_stmt_true_literal(source: str, snapshot: Any):
    """
    let x = 1
    if true {
        x = 3
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
    assert env.get("x") == 3


@docstring_source_with_snapshot
def test_if_stmt_false_literal(source: str, snapshot: Any):
    """
    let x = 1
    if false {
        x = 3
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
    assert env.get("x") == 1


@docstring_source_with_snapshot
def test_if_stmt_true_expr(source: str, snapshot: Any):
    """
    let x = 1
    if x == 1 {
        x = 3
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
    assert env.get("x") == 3


@docstring_source_with_snapshot
def test_if_else(source: str, snapshot: Any):
    """
    let x = ""
    if false {
        x = "true block"
    } else {
        x = "false block"
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
    assert env.get("x") == "false block"


@docstring_source_with_snapshot
def test_if_else_if(source: str, snapshot: Any):
    """
    let x = ""
    if false {
        x = "true block"
    } elif true {
        x = "elif block 1"
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
    assert env.get("x") == "elif block 1"


@docstring_source_with_snapshot
def test_if_else_if_2(source: str, snapshot: Any):
    """
    let x = ""
    if false {
        x = "true block"
    } elif false {
        x = "elif block 1"
    } elif true {
        x = "elif block 2"
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
    assert env.get("x") == "elif block 2"


@docstring_source_with_snapshot
def test_if_else_if_none_executes(source: str, snapshot: Any):
    """
    let x = ""
    if false {
        x = "true block"
    } elif false {
        x = "elif block 1"
    } elif false {
        x = "elif block 2"
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
    assert env.get("x") == ""


@docstring_source_with_snapshot
def test_if_else_if_else(source: str, snapshot: Any):
    """
    let x = ""
    if false {
        x = "true block"
    } elif false {
        x = "elif block 1"
    } elif false {
        x = "elif block 2"
    } else {
        x = "else block"
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
    assert env.get("x") == "else block"
