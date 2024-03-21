from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.langvalues import EnumValue
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    EnumLiteral,
    EnumMember,
    EnumMembers,
    EnumStmt,
    StatementList,
    VariableDeclaration,
)
from compiler.langtypes import Block, Enum, Type
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
    )
    assert type_env.get("Langs") == lang_type
    assert type_env.get("lang") == lang_type

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("lang") == EnumValue(ty="Langs", variant="English")
