from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    Assignment,
    BoolLiteral,
    Equality,
    IfStmt,
    IntLiteral,
    StatementBlock,
    StatementList,
    Variable,
    VariableDeclaration,
)
from compiler.langtypes import INT, Block, Bool, Int
from tests.utils import docstring_source


@docstring_source
def test_if_stmt_true_literal(source: str):
    """
    let x = 1
    if true {
        x = 3
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
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
                            StatementBlock: {
                                "stmts": [
                                    {
                                        Assignment: {
                                            "lvalue": "x",
                                            "rvalue": {IntLiteral: {"value": 3}},
                                        },
                                    }
                                ]
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
        StatementList: Block,
        "stmts": [
            {
                VariableDeclaration: Int,
                "rvalue": {IntLiteral: Int},
            },
            {
                IfStmt: Block,
                "cond": {BoolLiteral: Bool},
                "true_block": {
                    StatementBlock: Block,
                    "stmts": [
                        {
                            Assignment: Int,
                            "rvalue": {IntLiteral: Int},
                        }
                    ],
                },
            },
        ],
    }

    assert type_env.get("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 3


@docstring_source
def test_if_stmt_false_literal(source: str):
    """
    let x = 1
    if false {
        x = 3
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
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
                            StatementBlock: {
                                "stmts": [
                                    {
                                        Assignment: {
                                            "lvalue": "x",
                                            "rvalue": {IntLiteral: {"value": 3}},
                                        },
                                    }
                                ]
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
        StatementList: Block,
        "stmts": [
            {
                VariableDeclaration: Int,
                "rvalue": {IntLiteral: Int},
            },
            {
                IfStmt: Block,
                "cond": {BoolLiteral: Bool},
                "true_block": {
                    StatementBlock: Block,
                    "stmts": [
                        {
                            Assignment: Int,
                            "rvalue": {IntLiteral: Int},
                        }
                    ],
                },
            },
        ],
    }

    assert type_env.get("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 1


@docstring_source
def test_if_stmt_true_expr(source: str):
    """
    let x = 1
    if x == 1 {
        x = 3
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
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
                            StatementBlock: {
                                "stmts": [
                                    {
                                        Assignment: {
                                            "lvalue": "x",
                                            "rvalue": {IntLiteral: {"value": 3}},
                                        },
                                    }
                                ]
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
        StatementList: Block,
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
                    StatementBlock: Block,
                    "stmts": [
                        {
                            Assignment: Int,
                            "rvalue": {IntLiteral: Int},
                        }
                    ],
                },
            },
        ],
    }

    assert type_env.get("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 3
