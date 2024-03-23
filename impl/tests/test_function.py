from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    Comparison,
    FunctionArgs,
    FunctionCall,
    FunctionParam,
    FunctionParams,
    FunctionDefinition,
    IfChain,
    IfStmt,
    IntLiteral,
    ReturnStmt,
    StatementBlock,
    StatementList,
    Term,
    Variable,
    VariableDeclaration,
)
from compiler.langtypes import (
    INT,
    Block,
    Bool,
    Function,
    Int,
    Params,
    ReturnBlock,
)
from tests.utils import docstring_source


@docstring_source
def test_function_def_zero_args(source: str):
    """
    fn one() -> int {
        return 1
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        FunctionDefinition: {
            "name": "one",
            "return_type": "int",
            "body": {
                StatementBlock: {
                    "stmts": [
                        {ReturnStmt: {"return_value": {IntLiteral: {"value": 1}}}}
                    ]
                }
            },
        }
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == {
        FunctionDefinition: Function,
        "body": {
            StatementBlock: ReturnBlock,
            "stmts": [
                {
                    ReturnStmt: ReturnBlock,
                    "return_value": {
                        IntLiteral: Int,
                    },
                }
            ],
        },
    }

    assert type_env.get("one") == Function(
        function_name="one", arguments=Params([]), return_type=INT
    )


@docstring_source
def test_function_def_one_arg(source: str):
    """
    fn identity(a: int) -> int {
        return a
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        FunctionDefinition: {
            "name": "identity",
            "args": {
                FunctionParams: {
                    "args": [
                        {FunctionParam: {"name": "a", "arg_type": "int"}},
                    ]
                }
            },
            "return_type": "int",
            "body": {
                StatementBlock: {
                    "stmts": [
                        {ReturnStmt: {"return_value": {Variable: {"value": "a"}}}}
                    ]
                }
            },
        }
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == {
        FunctionDefinition: Function,
        "args": {
            FunctionParams: Params,
            "args": [{FunctionParam: Int}],
        },
        "body": {
            StatementBlock: ReturnBlock,
            "stmts": [
                {
                    ReturnStmt: ReturnBlock,
                    "return_value": {
                        Variable: Int,
                    },
                }
            ],
        },
    }

    assert type_env.get("identity") == Function(
        function_name="identity", arguments=Params([INT]), return_type=INT
    )


@docstring_source
def test_function_def_multiple_args(source: str):
    """
    fn sum(a: int, b: int) -> int {
        return a + b
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        FunctionDefinition: {
            "name": "sum",
            "args": {
                FunctionParams: {
                    "args": [
                        {FunctionParam: {"name": "a", "arg_type": "int"}},
                        {FunctionParam: {"name": "b", "arg_type": "int"}},
                    ]
                }
            },
            "return_type": "int",
            "body": {
                StatementBlock: {
                    "stmts": [
                        {
                            ReturnStmt: {
                                "return_value": {
                                    Term: {
                                        "left": {Variable: {"value": "a"}},
                                        "op": "+",
                                        "right": {Variable: {"value": "b"}},
                                    }
                                }
                            }
                        }
                    ]
                }
            },
        }
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == {
        FunctionDefinition: Function,
        "args": {
            FunctionParams: Params,
            "args": [{FunctionParam: Int}, {FunctionParam: Int}],
        },
        "body": {
            StatementBlock: ReturnBlock,
            "stmts": [
                {
                    ReturnStmt: ReturnBlock,
                    "return_value": {
                        Term: Int,
                        "left": {Variable: Int},
                        "right": {Variable: Int},
                    },
                }
            ],
        },
    }

    assert type_env.get("sum") == Function(
        function_name="sum", arguments=Params([INT, INT]), return_type=INT
    )


@docstring_source
def test_function_def_multiple_returns(source: str):
    """
    fn max(a: int, b: int) -> int {
        if a > b {
            return a
        } else {
            return b
        }
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        FunctionDefinition: {
            "name": "max",
            "args": {
                FunctionParams: {
                    "args": [
                        {FunctionParam: {"name": "a", "arg_type": "int"}},
                        {FunctionParam: {"name": "b", "arg_type": "int"}},
                    ]
                }
            },
            "return_type": "int",
            "body": {
                StatementBlock: {
                    "stmts": [
                        {
                            IfChain: {
                                "if_stmt": {
                                    IfStmt: {
                                        "cond": {
                                            Comparison: {
                                                "left": {Variable: {"value": "a"}},
                                                "op": ">",
                                                "right": {Variable: {"value": "b"}},
                                            }
                                        },
                                        "true_block": {
                                            StatementBlock: {
                                                "stmts": [
                                                    {
                                                        ReturnStmt: {
                                                            "return_value": {
                                                                Variable: {"value": "a"}
                                                            }
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
                                                ReturnStmt: {
                                                    "return_value": {
                                                        Variable: {"value": "b"}
                                                    }
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
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == {
        FunctionDefinition: Function,
        "args": {
            FunctionParams: Params,
            "args": [{FunctionParam: Int}, {FunctionParam: Int}],
        },
        "body": {
            StatementBlock: ReturnBlock,
            "stmts": [
                {
                    IfChain: ReturnBlock,
                    "if_stmt": {
                        IfStmt: ReturnBlock,
                        "cond": {
                            Comparison: Bool,
                            "left": {Variable: Int},
                            "right": {Variable: Int},
                        },
                        "true_block": {
                            StatementBlock: ReturnBlock,
                            "stmts": [
                                {
                                    ReturnStmt: ReturnBlock,
                                    "return_value": {Variable: Int},
                                }
                            ],
                        },
                    },
                    "else_block": {
                        StatementBlock: ReturnBlock,
                        "stmts": [
                            {ReturnStmt: ReturnBlock, "return_value": {Variable: Int}}
                        ],
                    },
                }
            ],
        },
    }

    assert type_env.get("max") == Function(
        function_name="max", arguments=Params([INT, INT]), return_type=INT
    )


@docstring_source
def test_function_call_zero_args(source: str):
    """
    fn one() -> int {
        return 1
    }

    let o = one()
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    FunctionDefinition: {
                        "name": "one",
                        "return_type": "int",
                        "body": {
                            StatementBlock: {
                                "stmts": [
                                    {
                                        ReturnStmt: {
                                            "return_value": {IntLiteral: {"value": 1}}
                                        }
                                    }
                                ]
                            }
                        },
                    }
                },
                {
                    VariableDeclaration: {
                        "ident": "o",
                        "rvalue": {
                            FunctionCall: {"callee": {Variable: {"value": "one"}}}
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
                FunctionDefinition: Function,
                "body": {
                    StatementBlock: ReturnBlock,
                    "stmts": [
                        {ReturnStmt: ReturnBlock, "return_value": {IntLiteral: Int}}
                    ],
                },
            },
            {
                VariableDeclaration: Int,
                "rvalue": {FunctionCall: Int, "callee": {Variable: Function}},
            },
        ],
    }

    assert type_env.get("one") == Function(
        function_name="one", arguments=Params([]), return_type=INT
    )

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("o") == 1


@docstring_source
def test_function_call_one_arg(source: str):
    """
    fn identity(a: int) -> int {
        return a
    }

    let i = identity(8)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    FunctionDefinition: {
                        "name": "identity",
                        "args": {
                            FunctionParams: {
                                "args": [
                                    {FunctionParam: {"name": "a", "arg_type": "int"}}
                                ]
                            }
                        },
                        "return_type": "int",
                        "body": {
                            StatementBlock: {
                                "stmts": [
                                    {
                                        ReturnStmt: {
                                            "return_value": {Variable: {"value": "a"}}
                                        }
                                    }
                                ]
                            }
                        },
                    }
                },
                {
                    VariableDeclaration: {
                        "ident": "i",
                        "rvalue": {
                            FunctionCall: {
                                "callee": {Variable: {"value": "identity"}},
                                "args": {
                                    FunctionArgs: {"args": [{IntLiteral: {"value": 8}}]}
                                },
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
                FunctionDefinition: Function,
                "args": {FunctionParams: Params, "args": [{FunctionParam: Int}]},
                "body": {
                    StatementBlock: ReturnBlock,
                    "stmts": [
                        {ReturnStmt: ReturnBlock, "return_value": {Variable: Int}}
                    ],
                },
            },
            {
                VariableDeclaration: Int,
                "rvalue": {
                    FunctionCall: Int,
                    "callee": {Variable: Function},
                    "args": {FunctionArgs: Params, "args": [{IntLiteral: Int}]},
                },
            },
        ],
    }

    assert type_env.get("identity") == Function(
        function_name="identity", arguments=Params([INT]), return_type=INT
    )

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("i") == 8


@docstring_source
def test_function_call_multiple_args(source: str):
    """
    fn sum(a: int, b: int) -> int {
        return a + b
    }

    let s = sum(1, 2)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    FunctionDefinition: {
                        "name": "sum",
                        "args": {
                            FunctionParams: {
                                "args": [
                                    {FunctionParam: {"name": "a", "arg_type": "int"}},
                                    {FunctionParam: {"name": "b", "arg_type": "int"}},
                                ]
                            }
                        },
                        "return_type": "int",
                        "body": {
                            StatementBlock: {
                                "stmts": [
                                    {
                                        ReturnStmt: {
                                            "return_value": {
                                                Term: {
                                                    "left": {Variable: {"value": "a"}},
                                                    "op": "+",
                                                    "right": {Variable: {"value": "b"}},
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                    }
                },
                {
                    VariableDeclaration: {
                        "ident": "s",
                        "rvalue": {
                            FunctionCall: {
                                "callee": {Variable: {"value": "sum"}},
                                "args": {
                                    FunctionArgs: {
                                        "args": [
                                            {IntLiteral: {"value": 1}},
                                            {IntLiteral: {"value": 2}},
                                        ]
                                    }
                                },
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
                FunctionDefinition: Function,
                "args": {
                    FunctionParams: Params,
                    "args": [{FunctionParam: Int}, {FunctionParam: Int}],
                },
                "body": {
                    StatementBlock: ReturnBlock,
                    "stmts": [
                        {
                            ReturnStmt: ReturnBlock,
                            "return_value": {
                                Term: Int,
                                "left": {Variable: Int},
                                "right": {Variable: Int},
                            },
                        }
                    ],
                },
            },
            {
                VariableDeclaration: Int,
                "rvalue": {
                    FunctionCall: Int,
                    "callee": {Variable: Function},
                    "args": {
                        FunctionArgs: Params,
                        "args": [{IntLiteral: Int}, {IntLiteral: Int}],
                    },
                },
            },
        ],
    }

    assert type_env.get("sum") == Function(
        function_name="sum", arguments=Params([INT, INT]), return_type=INT
    )

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("s") == 3


@docstring_source
def test_function_call_multiple_returns(source: str):
    """
    fn max(a: int, b: int) -> int {
        if a > b {
            return a
        } else {
            return b
        }
    }

    let m = max(3, 9)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    FunctionDefinition: {
                        "name": "max",
                        "args": {
                            FunctionParams: {
                                "args": [
                                    {FunctionParam: {"name": "a", "arg_type": "int"}},
                                    {FunctionParam: {"name": "b", "arg_type": "int"}},
                                ]
                            }
                        },
                        "return_type": "int",
                        "body": {
                            StatementBlock: {
                                "stmts": [
                                    {
                                        IfChain: {
                                            "if_stmt": {
                                                IfStmt: {
                                                    "cond": {
                                                        Comparison: {
                                                            "left": {
                                                                Variable: {"value": "a"}
                                                            },
                                                            "op": ">",
                                                            "right": {
                                                                Variable: {"value": "b"}
                                                            },
                                                        }
                                                    },
                                                    "true_block": {
                                                        StatementBlock: {
                                                            "stmts": [
                                                                {
                                                                    ReturnStmt: {
                                                                        "return_value": {
                                                                            Variable: {
                                                                                "value": "a"
                                                                            }
                                                                        }
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
                                                            ReturnStmt: {
                                                                "return_value": {
                                                                    Variable: {
                                                                        "value": "b"
                                                                    }
                                                                }
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
                {
                    VariableDeclaration: {
                        "ident": "m",
                        "rvalue": {
                            FunctionCall: {
                                "callee": {Variable: {"value": "max"}},
                                "args": {
                                    FunctionArgs: {
                                        "args": [
                                            {IntLiteral: {"value": 3}},
                                            {IntLiteral: {"value": 9}},
                                        ]
                                    }
                                },
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
                FunctionDefinition: Function,
                "args": {
                    FunctionParams: Params,
                    "args": [{FunctionParam: Int}, {FunctionParam: Int}],
                },
                "body": {
                    StatementBlock: ReturnBlock,
                    "stmts": [
                        {
                            IfChain: ReturnBlock,
                            "if_stmt": {
                                IfStmt: ReturnBlock,
                                "cond": {
                                    Comparison: Bool,
                                    "left": {Variable: Int},
                                    "right": {Variable: Int},
                                },
                                "true_block": {
                                    StatementBlock: ReturnBlock,
                                    "stmts": [
                                        {
                                            ReturnStmt: ReturnBlock,
                                            "return_value": {Variable: Int},
                                        }
                                    ],
                                },
                            },
                            "else_block": {
                                StatementBlock: ReturnBlock,
                                "stmts": [
                                    {
                                        ReturnStmt: ReturnBlock,
                                        "return_value": {Variable: Int},
                                    }
                                ],
                            },
                        }
                    ],
                },
            },
            {
                VariableDeclaration: Int,
                "rvalue": {
                    FunctionCall: Int,
                    "callee": {Variable: Function},
                    "args": {
                        FunctionArgs: Params,
                        "args": [{IntLiteral: Int}, {IntLiteral: Int}],
                    },
                },
            },
        ],
    }

    assert type_env.get("max") == Function(
        function_name="max", arguments=Params([INT, INT]), return_type=INT
    )

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("m") == 9
