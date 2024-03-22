from compiler.env import TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    Comparison,
    FunctionArg,
    FunctionArgs,
    FunctionDefinition,
    IfChain,
    IfStmt,
    IntLiteral,
    ReturnStmt,
    StatementBlock,
    Term,
    Variable,
)
from compiler.langtypes import (
    INT,
    Bool,
    Function,
    Int,
    Placeholder,
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
        function_name="one", arguments=[], return_type=INT
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
                FunctionArgs: {
                    "args": [
                        {FunctionArg: {"name": "a", "arg_type": "int"}},
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
            FunctionArgs: Placeholder,
            "args": [{FunctionArg: Int}],
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
        function_name="identity", arguments=[INT], return_type=INT
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
                FunctionArgs: {
                    "args": [
                        {FunctionArg: {"name": "a", "arg_type": "int"}},
                        {FunctionArg: {"name": "b", "arg_type": "int"}},
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
            FunctionArgs: Placeholder,
            "args": [{FunctionArg: Int}, {FunctionArg: Int}],
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
        function_name="sum", arguments=[INT, INT], return_type=INT
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
                FunctionArgs: {
                    "args": [
                        {FunctionArg: {"name": "a", "arg_type": "int"}},
                        {FunctionArg: {"name": "b", "arg_type": "int"}},
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
            FunctionArgs: Placeholder,
            "args": [{FunctionArg: Int}, {FunctionArg: Int}],
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
        function_name="max", arguments=[INT, INT], return_type=INT
    )
