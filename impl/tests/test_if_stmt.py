from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    Assignment,
    BoolLiteral,
    Equality,
    IfStmt,
    IntLiteral,
    StatementBlock,
    Variable,
    VariableDeclaration,
)
from compiler.langtypes import INT, Block, Bool, Int
from textwrap import dedent


def test_if_stmt_true_literal():
    """
    let x = 1
    if true {
        x = 3
    }
    """
    source = dedent(test_if_stmt_true_literal.__doc__).strip()  # type: ignore
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementBlock: {
            "stmts": [
                {
                    VariableDeclaration: {
                        "ident": "x",
                        "rvalue": {IntLiteral: {"value": 1}},
                    },
                },
                {
                    IfStmt: {
                        "cond": {BoolLiteral: {"value": True}},
                        "true_block": {
                            Assignment: {
                                "lvalue": "x",
                                "rvalue": {IntLiteral: {"value": 3}},
                            },
                        },
                    },
                },
            ],
        },
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == {
        StatementBlock: Block,
        "stmts": [
            {
                VariableDeclaration: Int,
                "rvalue": {IntLiteral: Int},
            },
            {
                IfStmt: Block,
                "cond": {BoolLiteral: Bool},
                "true_block": {
                    Assignment: Int,
                    "rvalue": {IntLiteral: Int},
                },
            },
        ],
    }

    assert type_env.get("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 3


def test_if_stmt_false_literal():
    """
    let x = 1
    if false {
        x = 3
    }
    """
    source = dedent(test_if_stmt_false_literal.__doc__).strip()  # type: ignore
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementBlock: {
            "stmts": [
                {
                    VariableDeclaration: {
                        "ident": "x",
                        "rvalue": {IntLiteral: {"value": 1}},
                    },
                },
                {
                    IfStmt: {
                        "cond": {BoolLiteral: {"value": False}},
                        "true_block": {
                            Assignment: {
                                "lvalue": "x",
                                "rvalue": {IntLiteral: {"value": 3}},
                            },
                        },
                    },
                },
            ],
        },
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == {
        StatementBlock: Block,
        "stmts": [
            {
                VariableDeclaration: Int,
                "rvalue": {IntLiteral: Int},
            },
            {
                IfStmt: Block,
                "cond": {BoolLiteral: Bool},
                "true_block": {
                    Assignment: Int,
                    "rvalue": {IntLiteral: Int},
                },
            },
        ],
    }

    assert type_env.get("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 1


def test_if_stmt_true_expr():
    """
    let x = 1
    if x == 1 {
        x = 3
    }
    """
    source = dedent(test_if_stmt_true_expr.__doc__).strip()  # type: ignore
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementBlock: {
            "stmts": [
                {
                    VariableDeclaration: {
                        "ident": "x",
                        "rvalue": {IntLiteral: {"value": 1}},
                    },
                },
                {
                    IfStmt: {
                        "cond": {
                            Equality: {
                                "left": {Variable: {"value": "x"}},
                                "op": "==",
                                "right": {
                                    IntLiteral: {"value": 1},
                                },
                            },
                        },
                        "true_block": {
                            Assignment: {
                                "lvalue": "x",
                                "rvalue": {IntLiteral: {"value": 3}},
                            },
                        },
                    },
                },
            ],
        },
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == {
        StatementBlock: Block,
        "stmts": [
            {
                VariableDeclaration: Int,
                "rvalue": {IntLiteral: Int},
            },
            {
                IfStmt: Block,
                "cond": {
                    Equality: Bool,
                    "left": {Variable: Int},
                    "right": {IntLiteral: Int},
                },
                "true_block": {
                    Assignment: Int,
                    "rvalue": {IntLiteral: Int},
                },
            },
        ],
    }

    assert type_env.get("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 3
