from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    Assignment,
    BoolLiteral,
    ElseIfLadder,
    ElseIfStmt,
    Equality,
    IfStmt,
    IntLiteral,
    StatementBlock,
    StatementList,
    StringLiteral,
    Variable,
    VariableDeclaration,
)
from compiler.langtypes import INT, STRING, Block, Bool, Int, String
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


@docstring_source
def test_if_else(source: str):
    """
    let x = ""
    if false {
        x = "true block"
    } else {
        x = "false block"
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    VariableDeclaration: {
                        "ident": "x",
                        "rvalue": {StringLiteral: {"value": ""}},
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
                                            "rvalue": {
                                                StringLiteral: {"value": "true block"}
                                            },
                                        },
                                    }
                                ]
                            },
                        },
                        "else_block": {
                            StatementBlock: {
                                "stmts": [
                                    {
                                        Assignment: {
                                            "lvalue": "x",
                                            "rvalue": {
                                                StringLiteral: {"value": "false block"}
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
                            Assignment: String,
                            "rvalue": {StringLiteral: String},
                        }
                    ],
                },
                "else_block": {
                    StatementBlock: Block,
                    "stmts": [
                        {
                            Assignment: String,
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
    assert env.get("x") == "false block"


@docstring_source
def test_if_else_if(source: str):
    """
    let x = ""
    if false {
        x = "true block"
    } else if true {
        x = "else if block 1"
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    VariableDeclaration: {
                        "ident": "x",
                        "rvalue": {StringLiteral: {"value": ""}},
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
                                            "rvalue": {
                                                StringLiteral: {"value": "true block"}
                                            },
                                        },
                                    }
                                ]
                            },
                        },
                        "else_if_ladder": {
                            ElseIfLadder: {
                                "blocks": [
                                    {
                                        ElseIfStmt: {
                                            "cond": {BoolLiteral: {"value": True}},
                                            "true_block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "x",
                                                                "rvalue": {
                                                                    StringLiteral: {
                                                                        "value": "else if block 1"
                                                                    }
                                                                },
                                                            },
                                                        }
                                                    ]
                                                },
                                            },
                                        }
                                    }
                                ],
                            }
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
                            Assignment: String,
                            "rvalue": {StringLiteral: String},
                        }
                    ],
                },
                "else_if_ladder": {
                    "blocks": [
                        {
                            ElseIfStmt: Block,
                            StatementBlock: Block,
                            "stmts": [
                                {
                                    Assignment: String,
                                    "rvalue": {StringLiteral: String},
                                }
                            ],
                        }
                    ],
                },
            },
        ],
    }

    assert type_env.get("x") == STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == "false block"
