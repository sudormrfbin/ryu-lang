from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()


def test_true_literal(snapshot: Any):
    ast = parse_tree_to_ast(parse("true"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_false_literal(snapshot: Any):
    ast = parse_tree_to_ast(parse("false"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


def test_int_literal(snapshot: Any):
    ast = parse_tree_to_ast(parse("123"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 123


def test_negative_signed_int_literal(snapshot: Any):
    ast = parse_tree_to_ast(parse("-1"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == -1


def test_positive_signed_int_literal(snapshot: Any):
    ast = parse_tree_to_ast(parse("+1"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 1


def test_string_literal(snapshot: Any):
    ast = parse_tree_to_ast(parse('"string"'))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == "string"


def test_string_with_spaces_literal(snapshot: Any):
    ast = parse_tree_to_ast(parse('"string with spaces"'))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == "string with spaces"


def test_empty_string_literal(snapshot: Any):
    ast = parse_tree_to_ast(parse('""'))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == ""
