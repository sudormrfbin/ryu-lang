from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    Assignment,
    Equality,
    IntLiteral,
    StatementBlock,
    StatementList,
    Term,
    Variable,
    VariableDeclaration,
    WhileStmt,
)
from compiler.langtypes import INT, Block, Bool, Int
from tests.utils import docstring_source


@docstring_source
def test_while_stmt(source: str):
    """
    //ignore
    let x = 5
    while x!=0 {
        x = x-1
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    VariableDeclaration: {
                        "ident": "x",
                        "rvalue": {IntLiteral: {"value": 5}},
                    }
                },
                {
                    WhileStmt: {
                        "cond": {
                            Equality: {
                                "left": {Variable: {"value": "x"}},
                                "op": "!=",
                                "right": {IntLiteral: {"value": 0}},
                            }
                        },
                        "true_block": {
                            StatementBlock: {
                                "stmts": [
                                    {
                                        Assignment: {
                                            "lvalue": "x",
                                            "rvalue": {
                                                Term: {
                                                    "left": {Variable: {"value": "x"}},
                                                    "op": "-",
                                                    "right": {IntLiteral: {"value": 1}},
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
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == {
        StatementList: Block,
        "stmts": [
            {VariableDeclaration: Int, "rvalue": {IntLiteral: Int}},
            {
                WhileStmt: Block,
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
                            "rvalue": {
                                Term: Int,
                                "left": {Variable: Int},
                                "right": {IntLiteral: Int},
                            },
                        }
                    ],
                },
            },
        ],
    }
    assert type_env.get("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 0
