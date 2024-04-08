from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.langvalues import StructValue
from compiler.parser import parse, parse_tree_to_ast
from compiler.langtypes import INT, STRING, Members, Struct
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
        members=Members({"name": STRING, "age": INT}),
    )


@docstring_source_with_snapshot
def test_struct_init(source: str, snapshot: Any):
    """
    struct Person {
        name: string
        age: int
    }

    let p = Person(name="bob", age=23)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("p") == StructValue(
        name="Person",
        attrs={
            "name": "bob",
            "age": 23,
        },
    )
