from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    Assignment,
    BoolLiteral,
    CaseLadder,
    CaseStmt,
    IntLiteral,
    MatchStmt,
    StatementBlock,
    StatementList,
    UnaryOp,
    VariableDeclaration,
)
from compiler.langtypes import INT, Block, Bool, Int
from tests.utils import docstring_source


@docstring_source
def test_match_case_bool(source: str):
    """
    let result = -1

    match true {
        case true { result = 1 }
        case false { result = 0 }
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    VariableDeclaration: {
                        "ident": "result",
                        "rvalue": {
                            UnaryOp: {"op": "-", "operand": {IntLiteral: {"value": 1}}}
                        },
                    }
                },
                {
                    MatchStmt: {
                        "expr": {BoolLiteral: {"value": True}},
                        "cases": {
                            CaseLadder: {
                                "cases": [
                                    {
                                        CaseStmt: {
                                            "pattern": {BoolLiteral: {"value": True}},
                                            "block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "result",
                                                                "rvalue": {
                                                                    IntLiteral: {
                                                                        "value": 1
                                                                    }
                                                                },
                                                            }
                                                        }
                                                    ]
                                                }
                                            },
                                        }
                                    },
                                    {
                                        CaseStmt: {
                                            "pattern": {BoolLiteral: {"value": False}},
                                            "block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "result",
                                                                "rvalue": {
                                                                    IntLiteral: {
                                                                        "value": 0
                                                                    }
                                                                },
                                                            }
                                                        }
                                                    ]
                                                }
                                            },
                                        }
                                    },
                                ]
                            }
                        },
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
            {
                VariableDeclaration: Int,
                "rvalue": {UnaryOp: Int, "operand": {IntLiteral: Int}},
            },
            {
                MatchStmt: Block,
                "expr": {BoolLiteral: Bool},
                "cases": {
                    CaseLadder: Block,
                    "cases": [
                        {
                            CaseStmt: Bool,
                            "pattern": {BoolLiteral: Bool},
                            "block": {
                                StatementBlock: Block,
                                "stmts": [
                                    {Assignment: Int, "rvalue": {IntLiteral: Int}}
                                ],
                            },
                        },
                        {
                            CaseStmt: Bool,
                            "pattern": {BoolLiteral: Bool},
                            "block": {
                                StatementBlock: Block,
                                "stmts": [
                                    {Assignment: Int, "rvalue": {IntLiteral: Int}}
                                ],
                            },
                        },
                    ],
                },
            },
        ],
    }

    assert type_env.get("result") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("result") == 1
