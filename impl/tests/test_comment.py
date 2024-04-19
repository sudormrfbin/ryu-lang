from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    Assignment,
    BoolLiteral,
    IfChain,
    IfStmt,
    IntLiteral,
    StatementBlock,
    StatementList,
    VariableDeclaration,
)
from compiler.langtypes import INT, Block, Bool, Int
from tests.utils import docstring_source


@docstring_source
def test_if_stmt_true_literal(source: str):
    """
    //ignore
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
                    }
                },
                {
                    IfChain: {
                        "if_stmt": {
                            IfStmt: {
                                "cond": {BoolLiteral: {"value": True}},
                                "true_block": {
                                    StatementBlock: {
                                        "stmts": [
                                            {
                                                Assignment: {
                                                    "lvalue": "x",
                                                    "rvalue": {
                                                        IntLiteral: {"value": 3}
                                                    },
                                                }
                                            }
                                        ]
                                    }
                                },
                            }
                        }
                    }
                },
            ]
        }
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == {
        StatementList: Block,
        "stmts": [
            {VariableDeclaration: Int, "rvalue": {IntLiteral: Int}},
            {
                IfChain: Block,
                "if_stmt": {
                    IfStmt: Block,
                    "cond": {BoolLiteral: Bool},
                    "true_block": {
                        StatementBlock: Block,
                        "stmts": [{Assignment: Int, "rvalue": {IntLiteral: Int}}],
                    },
                },
            },
        ],
    }

    assert type_env.get_var_type("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 3


@docstring_source
def test_if_stmt_false_literal(source: str):
    """
    let x = 1 //ignore
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
                    }
                },
                {
                    IfChain: {
                        "if_stmt": {
                            IfStmt: {
                                "cond": {BoolLiteral: {"value": False}},
                                "true_block": {
                                    StatementBlock: {
                                        "stmts": [
                                            {
                                                Assignment: {
                                                    "lvalue": "x",
                                                    "rvalue": {
                                                        IntLiteral: {"value": 3}
                                                    },
                                                }
                                            }
                                        ]
                                    }
                                },
                            }
                        }
                    }
                },
            ]
        }
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == {
        StatementList: Block,
        "stmts": [
            {VariableDeclaration: Int, "rvalue": {IntLiteral: Int}},
            {
                IfChain: Block,
                "if_stmt": {
                    IfStmt: Block,
                    "cond": {BoolLiteral: Bool},
                    "true_block": {
                        StatementBlock: Block,
                        "stmts": [{Assignment: Int, "rvalue": {IntLiteral: Int}}],
                    },
                },
            },
        ],
    }

    assert type_env.get_var_type("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 1
