from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    BoolLiteral,
    IfStmt,
    IntLiteral,
    StatementBlock,
    StatementList,
    StringLiteral,
    VariableDeclaration,
)
from compiler.langtypes import STRING, Block, Bool, Int, String
from tests.utils import docstring_source


@docstring_source
def test_lexical_scope_variable_shadowing(source: str):
    """
    let x = "outside"
    if true {
        let x = "inside"
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    VariableDeclaration: {
                        "ident": "x",
                        "rvalue": {StringLiteral: {"value": "outside"}},
                    },
                },
                {
                    IfStmt: {
                        "cond": {BoolLiteral: {"value": True}},
                        "true_block": {
                            StatementBlock: {
                                "stmts": [
                                    {
                                        VariableDeclaration: {
                                            "ident": "x",
                                            "rvalue": {
                                                StringLiteral: {"value": "inside"}
                                            },
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
                VariableDeclaration: String,
                "rvalue": {StringLiteral: String},
            },
            {
                IfStmt: Block,
                "cond": {BoolLiteral: Bool},
                "true_block": {
                    StatementBlock: Block,
                    "stmts": [
                        {
                            VariableDeclaration: String,
                            "rvalue": {StringLiteral: String},
                        }
                    ],
                },
            },
        ],
    }

    assert type_env.get("x") == STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    print(vars(env))
    assert env.get("x") == "outside"


@docstring_source
def test_lexical_scope_variable_type(source: str):
    """
    let x = "outside"
    if true {
        let x = 8
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    VariableDeclaration: {
                        "ident": "x",
                        "rvalue": {StringLiteral: {"value": "outside"}},
                    },
                },
                {
                    IfStmt: {
                        "cond": {BoolLiteral: {"value": True}},
                        "true_block": {
                            StatementBlock: {
                                "stmts": [
                                    {
                                        VariableDeclaration: {
                                            "ident": "x",
                                            "rvalue": {IntLiteral: {"value": 8}},
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
                VariableDeclaration: String,
                "rvalue": {StringLiteral: String},
            },
            {
                IfStmt: Block,
                "cond": {BoolLiteral: Bool},
                "true_block": {
                    StatementBlock: Block,
                    "stmts": [
                        {
                            VariableDeclaration: Int,
                            "rvalue": {IntLiteral: Int},
                        }
                    ],
                },
            },
        ],
    }

    assert type_env.get("x") == STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    print(env)
    assert env.get("x") == "outside"
