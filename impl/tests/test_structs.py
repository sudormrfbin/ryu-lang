from typing import Any
from compiler.env import TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.langtypes import INT, STRING, Struct
from tests.utils import docstring_source_with_snapshot


# 1. struct type in typeenv


@docstring_source_with_snapshot
def test_struct_def(source: str, snapshot: Any):
    """
    struct Person {
        name: string
        age: int
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get("Person") == Struct(
        struct_name="Person",
        members={
            "name": STRING,
            "age": INT,
        },
    )
