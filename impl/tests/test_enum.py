from compiler import langtypes
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import Span
from compiler.langvalues import EnumValue
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    Assignment,
    CaseLadder,
    CaseStmt,
    EnumLiteral,
    EnumMember,
    EnumMembers,
    EnumStmt,
    MatchStmt,
    StatementBlock,
    StatementList,
    StringLiteral,
    Variable,
    VariableDeclaration,
)
from compiler.langtypes import Block, Enum, String, Type
from tests.utils import docstring_source


@docstring_source
def test_enum_def(source: str):
    """
    enum Langs {
        Malayalam
        English
        Japanese
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        EnumStmt: {
            "name": "Langs",
            "members": {
                EnumMembers: {
                    "members": [
                        {EnumMember: {"name": "Malayalam"}},
                        {EnumMember: {"name": "English"}},
                        {EnumMember: {"name": "Japanese"}},
                    ]
                }
            },
        }
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == {
        EnumStmt: Enum,
        "members": {
            EnumMembers: Block,
            "members": [
                {EnumMember: Type},
                {EnumMember: Type},
                {EnumMember: Type},
            ],
        },
    }

    assert type_env.get("Langs") == Enum(
        enum_name="Langs",
        members=["Malayalam", "English", "Japanese"],
        span=Span(start_line=1, end_line=1, start_column=6, end_column=11, start_pos=5, end_pos=10)
    )


@docstring_source
def test_enum_assignment(source: str):
    """
    enum Langs {
        Malayalam
        English
        Japanese
    }
    let lang = Langs::English
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    EnumStmt: {
                        "name": "Langs",
                        "members": {
                            EnumMembers: {
                                "members": [
                                    {EnumMember: {"name": "Malayalam"}},
                                    {EnumMember: {"name": "English"}},
                                    {EnumMember: {"name": "Japanese"}},
                                ]
                            }
                        },
                    }
                },
                {
                    VariableDeclaration: {
                        "ident": "lang",
                        "rvalue": {
                            EnumLiteral: {
                                "enum_type": "Langs",
                                "variant": "English",
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
            {
                EnumStmt: Enum,
                "members": {
                    EnumMembers: Block,
                    "members": [
                        {EnumMember: Type},
                        {EnumMember: Type},
                        {EnumMember: Type},
                    ],
                },
            },
            {
                VariableDeclaration: Enum,
                "rvalue": {EnumLiteral: Enum},
            },
        ],
    }

    lang_type = Enum(
        enum_name="Langs",
        members=["Malayalam", "English", "Japanese"],
        span=Span(start_line=1, end_line=1, start_column=6, end_column=11, start_pos=5, end_pos=10)
    )
    assert type_env.get("Langs") == lang_type
    assert type_env.get("lang") == lang_type

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("lang") == EnumValue(ty="Langs", variant="English")


@docstring_source
def test_enum_pattern_match(source: str):
    """
    enum Langs {
        Malayalam
        English
        Japanese
    }
    let lang = Langs::English

    let langcode = ""
    match lang {
        case Langs::English { langcode = "eng" }
        case Langs::Malayalam { langcode = "ml" }
        case Langs::Japanese { langcode = "jp" }
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementList: {
            "stmts": [
                {
                    EnumStmt: {
                        "name": "Langs",
                        "members": {
                            EnumMembers: {
                                "members": [
                                    {EnumMember: {"name": "Malayalam"}},
                                    {EnumMember: {"name": "English"}},
                                    {EnumMember: {"name": "Japanese"}},
                                ]
                            }
                        },
                    }
                },
                {
                    VariableDeclaration: {
                        "ident": "lang",
                        "rvalue": {
                            EnumLiteral: {"enum_type": "Langs", "variant": "English"}
                        },
                    }
                },
                {
                    VariableDeclaration: {
                        "ident": "langcode",
                        "rvalue": {StringLiteral: {"value": ""}},
                    }
                },
                {
                    MatchStmt: {
                        "expr": {Variable: {"value": "lang"}},
                        "cases": {
                            CaseLadder: {
                                "cases": [
                                    {
                                        CaseStmt: {
                                            "pattern": {
                                                EnumLiteral: {
                                                    "enum_type": "Langs",
                                                    "variant": "English",
                                                }
                                            },
                                            "block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "langcode",
                                                                "rvalue": {
                                                                    StringLiteral: {
                                                                        "value": "eng"
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
                                            "pattern": {
                                                EnumLiteral: {
                                                    "enum_type": "Langs",
                                                    "variant": "Malayalam",
                                                }
                                            },
                                            "block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "langcode",
                                                                "rvalue": {
                                                                    StringLiteral: {
                                                                        "value": "ml"
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
                                            "pattern": {
                                                EnumLiteral: {
                                                    "enum_type": "Langs",
                                                    "variant": "Japanese",
                                                }
                                            },
                                            "block": {
                                                StatementBlock: {
                                                    "stmts": [
                                                        {
                                                            Assignment: {
                                                                "lvalue": "langcode",
                                                                "rvalue": {
                                                                    StringLiteral: {
                                                                        "value": "jp"
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
                EnumStmt: Enum,
                "members": {
                    EnumMembers: Block,
                    "members": [
                        {EnumMember: Type},
                        {EnumMember: Type},
                        {EnumMember: Type},
                    ],
                },
            },
            {VariableDeclaration: Enum, "rvalue": {EnumLiteral: Enum}},
            {VariableDeclaration: String, "rvalue": {StringLiteral: String}},
            {
                MatchStmt: Block,
                "expr": {Variable: Enum},
                "cases": {
                    CaseLadder: Block,
                    "cases": [
                        {
                            CaseStmt: Enum,
                            "pattern": {EnumLiteral: Enum},
                            "block": {
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
                            CaseStmt: Enum,
                            "pattern": {EnumLiteral: Enum},
                            "block": {
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
                            CaseStmt: Enum,
                            "pattern": {EnumLiteral: Enum},
                            "block": {
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

    lang_type = Enum(
        enum_name="Langs",
        members=["Malayalam", "English", "Japanese"],
        span=Span(start_line=1, end_line=1, start_column=6, end_column=11, start_pos=5, end_pos=10)
    )
    assert type_env.get("Langs") == lang_type
    assert type_env.get("lang") == lang_type
    assert type_env.get("langcode") == langtypes.STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("lang") == EnumValue(ty="Langs", variant="English")
    assert env.get("langcode") == "eng"
