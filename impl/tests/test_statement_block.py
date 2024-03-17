from compiler.env import TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import IntLiteral, StatementList
from compiler.langtypes import Block, Int


EMPTY_TYPE_ENV = TypeEnvironment()


def test_statement_without_newline_fallsthrough_to_expression():
    ast = parse_tree_to_ast(parse("1"))
    assert ast.to_dict() == {IntLiteral: {"value": 1}}
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == {IntLiteral: Int}


def test_statement_with_single_newline_fallsthrough_to_expression():
    # since there is only one statement, it fallsthrough
    ast = parse_tree_to_ast(parse("1\n"))
    assert ast.to_dict() == {IntLiteral: {"value": 1}}
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == {IntLiteral: Int}


def test_statement_with_multiple_newlines_fallsthrough_to_expression():
    ast = parse_tree_to_ast(parse("1\n\n"))
    assert ast.to_dict() == {IntLiteral: {"value": 1}}
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == {IntLiteral: Int}


def test_block_with_multiple_statements():
    ast = parse_tree_to_ast(parse("1\n2"))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {IntLiteral: {"value": 1}},
                {IntLiteral: {"value": 2}},
            ]
        }
    }
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == {
        StatementList: Block,
        "stmts": [
            {IntLiteral: Int},
            {IntLiteral: Int},
        ],
    }


def test_block_with_multiple_statements_and_trailing_newline():
    ast = parse_tree_to_ast(parse("1\n2\n"))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {IntLiteral: {"value": 1}},
                {IntLiteral: {"value": 2}},
            ]
        }
    }
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == {
        StatementList: Block,
        "stmts": [
            {IntLiteral: Int},
            {IntLiteral: Int},
        ],
    }
