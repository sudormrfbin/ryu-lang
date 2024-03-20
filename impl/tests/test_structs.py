from compiler.env import TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    StructMember,
    StructMembers,
    StructStmt,
)
from compiler.langtypes import INT, STRING, Block, Int, String, Struct
from tests.utils import docstring_source


# 1. struct type in typeenv


@docstring_source
def test_struct_def(source: str):
    """
    struct Person {
        name: string
        age: int
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StructStmt: {
            "name": "Person",
            "members": {
                StructMembers: {
                    "members": [
                        {
                            StructMember: {
                                "name": "name",
                                "ident_type": "string",
                            }
                        },
                        {
                            StructMember: {
                                "name": "age",
                                "ident_type": "int",
                            }
                        },
                    ]
                }
            },
        }
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == {
        StructStmt: Struct,
        "members": {
            StructMembers: Block,
            "members": [{StructMember: String}, {StructMember: Int}],
        },
    }

    assert type_env.get("Person") == Struct(
        struct_name="Person",
        members={
            "name": STRING,
            "age": INT,
        },
    )
