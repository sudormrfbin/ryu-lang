from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    Assignment,
    BoolLiteral,
    ElseIfLadder,
    ElseIfStmt,
    Equality,
    IfChain,
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
                    }
                },
                {
                    IfChain: {
                        "if_stmt": {
                            IfStmt: {
                                "cond": {
                                    Equality: {
                                        "left": {Variable: {"value": "x"}},
                                        "op": "==",
                                        "right": {IntLiteral: {"value": 1}},
                                    }
                                },
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
                    "cond": {
                        Equality: Bool,
                        "left": {Variable: Int},
                        "right": {IntLiteral: Int},
                    },
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
                                                        StringLiteral: {
                                                            "value": "true block"
                                                        }
                                                    },
                                                }
                                            }
                                        ]
                                    }
                                },
                            }
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
    assert ast.to_type_dict() == {
        StatementList: Block,
        "stmts": [
            {VariableDeclaration: String, "rvalue": {StringLiteral: String}},
            {
                IfChain: Block,
                "if_stmt": {
                    IfStmt: Block,
                    "cond": {BoolLiteral: Bool},
                    "true_block": {
                        StatementBlock: Block,
                        "stmts": [
                            {Assignment: String, "rvalue": {StringLiteral: String}}
                        ],
                    },
                },
                "else_block": {
                    StatementBlock: Block,
                    "stmts": [{Assignment: String, "rvalue": {StringLiteral: String}}],
                },
            },
        ],
    }

    assert type_env.get_var_type("x") == STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == "false block"


@docstring_source
def test_if_else_if(source: str):
    """
    let x = ""
    if false {
        x = "true block"
    } elif true {
        x = "elif block 1"
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
                                                        StringLiteral: {
                                                            "value": "true block"
                                                        }
                                                    },
                                                }
                                            }
                                        ]
                                    }
                                },
                            }
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
                                                                        "value": "elif block 1"
                                                                    }
                                                                },
                                                            }
                                                        }
                                                    ]
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
    assert ast.to_type_dict() == {
        StatementList: Block,
        "stmts": [
            {VariableDeclaration: String, "rvalue": {StringLiteral: String}},
            {
                IfChain: Block,
                "if_stmt": {
                    IfStmt: Block,
                    "cond": {BoolLiteral: Bool},
                    "true_block": {
                        StatementBlock: Block,
                        "stmts": [
                            {Assignment: String, "rvalue": {StringLiteral: String}}
                        ],
                    },
                },
                "else_if_ladder": {
                    ElseIfLadder: Block,
                    "blocks": [
                        {
                            ElseIfStmt: Block,
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
                        }
                    ],
                },
            },
        ],
    }

    assert type_env.get_var_type("x") == STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == "elif block 1"


@docstring_source
def test_if_else_if_2(source: str):
    """
    let x = ""
    if false {
        x = "true block"
    } elif false {
        x = "elif block 1"
    } elif true {
        x = "elif block 2"
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
                                                        StringLiteral: {
                                                            "value": "true block"
                                                        }
                                                    },
                                                }
                                            }
                                        ]
                                    }
                                },
                            }
                        },
                        "else_if_ladder": {
                            ElseIfLadder: {
                                "blocks": [
                                    {
                                        ElseIfStmt: {
                                            "cond": {BoolLiteral: {"value": False}},
                                            "true_block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "x",
                                                                "rvalue": {
                                                                    StringLiteral: {
                                                                        "value": "elif block 1"
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
                                                                        "value": "elif block 2"
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
            {VariableDeclaration: String, "rvalue": {StringLiteral: String}},
            {
                IfChain: Block,
                "if_stmt": {
                    IfStmt: Block,
                    "cond": {BoolLiteral: Bool},
                    "true_block": {
                        StatementBlock: Block,
                        "stmts": [
                            {Assignment: String, "rvalue": {StringLiteral: String}}
                        ],
                    },
                },
                "else_if_ladder": {
                    ElseIfLadder: Block,
                    "blocks": [
                        {
                            ElseIfStmt: Block,
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
                        },
                        {
                            ElseIfStmt: Block,
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
                        },
                    ],
                },
            },
        ],
    }

    assert type_env.get_var_type("x") == STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == "elif block 2"


@docstring_source
def test_if_else_if_none_executes(source: str):
    """
    let x = ""
    if false {
        x = "true block"
    } elif false {
        x = "elif block 1"
    } elif false {
        x = "elif block 2"
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
                                                        StringLiteral: {
                                                            "value": "true block"
                                                        }
                                                    },
                                                }
                                            }
                                        ]
                                    }
                                },
                            }
                        },
                        "else_if_ladder": {
                            ElseIfLadder: {
                                "blocks": [
                                    {
                                        ElseIfStmt: {
                                            "cond": {BoolLiteral: {"value": False}},
                                            "true_block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "x",
                                                                "rvalue": {
                                                                    StringLiteral: {
                                                                        "value": "elif block 1"
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
                                        ElseIfStmt: {
                                            "cond": {BoolLiteral: {"value": False}},
                                            "true_block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "x",
                                                                "rvalue": {
                                                                    StringLiteral: {
                                                                        "value": "elif block 2"
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
            {VariableDeclaration: String, "rvalue": {StringLiteral: String}},
            {
                IfChain: Block,
                "if_stmt": {
                    IfStmt: Block,
                    "cond": {BoolLiteral: Bool},
                    "true_block": {
                        StatementBlock: Block,
                        "stmts": [
                            {Assignment: String, "rvalue": {StringLiteral: String}}
                        ],
                    },
                },
                "else_if_ladder": {
                    ElseIfLadder: Block,
                    "blocks": [
                        {
                            ElseIfStmt: Block,
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
                        },
                        {
                            ElseIfStmt: Block,
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
                        },
                    ],
                },
            },
        ],
    }

    assert type_env.get_var_type("x") == STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == ""


@docstring_source
def test_if_else_if_else(source: str):
    """
    let x = ""
    if false {
        x = "true block"
    } elif false {
        x = "elif block 1"
    } elif false {
        x = "elif block 2"
    } else {
        x = "else block"
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
                                                        StringLiteral: {
                                                            "value": "true block"
                                                        }
                                                    },
                                                }
                                            }
                                        ]
                                    }
                                },
                            }
                        },
                        "else_if_ladder": {
                            ElseIfLadder: {
                                "blocks": [
                                    {
                                        ElseIfStmt: {
                                            "cond": {BoolLiteral: {"value": False}},
                                            "true_block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "x",
                                                                "rvalue": {
                                                                    StringLiteral: {
                                                                        "value": "elif block 1"
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
                                        ElseIfStmt: {
                                            "cond": {BoolLiteral: {"value": False}},
                                            "true_block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "x",
                                                                "rvalue": {
                                                                    StringLiteral: {
                                                                        "value": "elif block 2"
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
                        "else_block": {
                            StatementBlock: {
                                "stmts": [
                                    {
                                        Assignment: {
                                            "lvalue": "x",
                                            "rvalue": {
                                                StringLiteral: {"value": "else block"}
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
    assert ast.to_type_dict() == {
        StatementList: Block,
        "stmts": [
            {VariableDeclaration: String, "rvalue": {StringLiteral: String}},
            {
                IfChain: Block,
                "if_stmt": {
                    IfStmt: Block,
                    "cond": {BoolLiteral: Bool},
                    "true_block": {
                        StatementBlock: Block,
                        "stmts": [
                            {Assignment: String, "rvalue": {StringLiteral: String}}
                        ],
                    },
                },
                "else_if_ladder": {
                    ElseIfLadder: Block,
                    "blocks": [
                        {
                            ElseIfStmt: Block,
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
                        },
                        {
                            ElseIfStmt: Block,
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
                        },
                    ],
                },
                "else_block": {
                    StatementBlock: Block,
                    "stmts": [{Assignment: String, "rvalue": {StringLiteral: String}}],
                },
            },
        ],
    }

    assert type_env.get_var_type("x") == STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == "else block"
