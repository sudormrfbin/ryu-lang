from typing import Any
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
from tests.utils import docstring_source, docstring_source_with_snapshot


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


@docstring_source_with_snapshot
def test_enum_pattern_match_wildcard(source: str, snapshot: Any):
    """
    enum Langs {
        Malayalam
        English
        Japanese
    }

    fn is_eng(lang: Langs) -> bool {
        match lang {
            case Langs::English { return true }
            case _ { return false }
        }
    }

    let with_eng = is_eng(Langs::English)
    let with_mal = is_eng(Langs::Malayalam)
    let with_jp = is_eng(Langs::Japanese)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot(name="ast")

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot(name="typed-ast")

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("with_eng") is True
    assert env.get("with_mal") is False
    assert env.get("with_jp") is False


@docstring_source_with_snapshot
def test_match_array(source: str, snapshot: Any):
    """
    fn len(arr: array<int>) -> int {
        match arr {
            case [1] { return 1 }
            case [1, 2] { return 2 }
            case [1, 2, 3] { return 3 }
            case _ { return -1 }
        }
    }

    let one = len([1])
    let two = len([1, 2])
    let three = len([1, 2, 3])
    let more = len([1, 2, 3, 4])
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot(name="ast")

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot(name="typed-ast")

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("one") == 1
    assert env.get("two") == 2
    assert env.get("three") == 3
    assert env.get("more") == -1


@docstring_source_with_snapshot
def test_match_array_empty_case(source: str, snapshot: Any):
    """
    fn len(arr: array<int>) -> int {
        match arr {
            case [] { return 0 }
            case _ { return -1 }
        }
    }

    let zero = len(<int>[])
    let one = len([1])
    let two = len([1, 2])
    let three = len([1, 2, 3])
    let more = len([1, 2, 3, 4])
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot(name="ast")

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot(name="typed-ast")

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("zero") == 0
    assert env.get("one") == -1
    assert env.get("two") == -1
    assert env.get("three") == -1
    assert env.get("more") == -1
