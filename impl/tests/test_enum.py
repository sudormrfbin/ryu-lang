from compiler.env import TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    EnumMember,
    EnumMembers,
    EnumStmt,
    StructMember,
    StructMembers,
    StructStmt,
)
from compiler.langtypes import INT, STRING, Block, Enum, Int, String, Struct, Type
from tests.utils import docstring_source


# 1. struct type in typeenv


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
