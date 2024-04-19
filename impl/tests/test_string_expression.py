from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()


def test_string_concat_2(snapshot: Any):
    ast = parse_tree_to_ast(parse('"hello"+"world"'))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == "helloworld"


def test_string_concat_3(snapshot: Any):
    ast = parse_tree_to_ast(parse('"hello"+" "+"world"'))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == "hello world"
