from typing import Any
from compiler.env import TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import IntLiteral
from compiler.langtypes import Int


EMPTY_TYPE_ENV = TypeEnvironment()


def test_statement_without_newline_fallsthrough_to_expression(snapshot: Any):
    ast = parse_tree_to_ast(parse("1"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot


def test_statement_with_single_newline_fallsthrough_to_expression(snapshot: Any):
    # since there is only one statement, it fallsthrough
    ast = parse_tree_to_ast(parse("1\n"))
    assert ast.to_dict() == {IntLiteral: {"value": 1}}
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == {IntLiteral: Int}


def test_statement_with_multiple_newlines_fallsthrough_to_expression(snapshot: Any):
    ast = parse_tree_to_ast(parse("1\n\n"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot


def test_block_with_multiple_statements(snapshot: Any):
    ast = parse_tree_to_ast(parse("1\n2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot


def test_block_with_multiple_statements_and_trailing_newline(snapshot: Any):
    ast = parse_tree_to_ast(parse("1\n2\n"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
