from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.langtypes import (
    INT,
    Array,
    Function,
    Params,
)
from tests.utils import docstring_source_with_snapshot


@docstring_source_with_snapshot
def test_function_def_zero_args(source: str, snapshot: Any):
    """
    fn one() -> int {
        return 1
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == snapshot

    assert type_env.get("one") == Function(
        function_name="one", arguments=Params([]), return_type=INT
    )


@docstring_source_with_snapshot
def test_function_def_one_arg(source: str, snapshot: Any):
    """
    fn identity(a: int) -> int {
        return a
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == snapshot

    assert type_env.get("identity") == Function(
        function_name="identity", arguments=Params([INT]), return_type=INT
    )


@docstring_source_with_snapshot
def test_function_def_multiple_args(source: str, snapshot: Any):
    """
    fn sum(a: int, b: int) -> int {
        return a + b
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == snapshot

    assert type_env.get("sum") == Function(
        function_name="sum", arguments=Params([INT, INT]), return_type=INT
    )


@docstring_source_with_snapshot
def test_function_def_multiple_returns(source: str, snapshot: Any):
    """
    fn max(a: int, b: int) -> int {
        if a > b {
            return a
        } else {
            return b
        }
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == snapshot

    assert type_env.get("max") == Function(
        function_name="max", arguments=Params([INT, INT]), return_type=INT
    )


@docstring_source_with_snapshot
def test_function_call_zero_args(source: str, snapshot: Any):
    """
    fn one() -> int {
        return 1
    }

    let o = one()
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get("one") == Function(
        function_name="one", arguments=Params([]), return_type=INT
    )

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("o") == 1


@docstring_source_with_snapshot
def test_function_call_one_arg(source: str, snapshot: Any):
    """
    fn identity(a: int) -> int {
        return a
    }

    let i = identity(8)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get("identity") == Function(
        function_name="identity", arguments=Params([INT]), return_type=INT
    )

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("i") == 8


@docstring_source_with_snapshot
def test_function_call_multiple_args(source: str, snapshot: Any):
    """
    fn sum(a: int, b: int) -> int {
        return a + b
    }

    let s = sum(1, 2)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get("sum") == Function(
        function_name="sum", arguments=Params([INT, INT]), return_type=INT
    )

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("s") == 3


@docstring_source_with_snapshot
def test_function_call_multiple_returns(source: str, snapshot: Any):
    """
    fn max(a: int, b: int) -> int {
        if a > b {
            return a
        } else {
            return b
        }
    }

    let m = max(3, 9)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get("max") == Function(
        function_name="max", arguments=Params([INT, INT]), return_type=INT
    )

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("m") == 9


@docstring_source_with_snapshot
def test_function_def_array_arg(source: str, snapshot: Any):
    """
    fn one(arr: array<int>) -> int {
        return 1
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == snapshot

    assert type_env.get("one") == Function(
        function_name="one", arguments=Params([Array(INT)]), return_type=INT
    )

@docstring_source_with_snapshot
def test_function_recursive(source: str, snapshot: Any):
    """
    fn fact(n: int) -> int {
        if n <= 0 {
            return 1
        } else {
            return fact(n - 1) * n
        }
    }

    let x1 = fact(1)
    let x2 = fact(2)
    let x3 = fact(3)
    let x4 = fact(4)
    let x5 = fact(5)
    let x6 = fact(6)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == snapshot

    env = RuntimeEnvironment()
    ast.eval(env)

    assert env.get("x1") == 1
    assert env.get("x2") == 2
    assert env.get("x3") == 6
    assert env.get("x4") == 24
    assert env.get("x5") == 120
    assert env.get("x6") == 720
    