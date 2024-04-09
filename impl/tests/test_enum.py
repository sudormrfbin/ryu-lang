from typing import Any
from compiler import langtypes
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import Span
from compiler.langtypes import Enum
from compiler.langvalues import EnumValue
from compiler.parser import parse, parse_tree_to_ast
from tests.utils import docstring_source_with_snapshot


@docstring_source_with_snapshot
def test_enum_def(source: str, snapshot: Any):
    """
    enum Langs {
        Malayalam
        English
        Japanese
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get("Langs") == Enum(
        enum_name="Langs",
        members=["Malayalam", "English", "Japanese"],
        span=Span(
            start_line=1,
            end_line=1,
            start_column=6,
            end_column=11,
            start_pos=5,
            end_pos=10,
        ),
    )


@docstring_source_with_snapshot
def test_enum_assignment(source: str, snapshot: Any):
    """
    enum Langs {
        Malayalam
        English
        Japanese
    }
    let lang = Langs::English
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == snapshot

    lang_type = Enum(
        enum_name="Langs",
        members=["Malayalam", "English", "Japanese"],
        span=Span(
            start_line=1,
            end_line=1,
            start_column=6,
            end_column=11,
            start_pos=5,
            end_pos=10,
        ),
    )
    assert type_env.get("Langs") == lang_type
    assert type_env.get("lang") == lang_type

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("lang") == EnumValue(ty="Langs", variant="English")


@docstring_source_with_snapshot
def test_enum_pattern_match(source: str, snapshot: Any):
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
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    lang_type = Enum(
        enum_name="Langs",
        members=["Malayalam", "English", "Japanese"],
        span=Span(
            start_line=1,
            end_line=1,
            start_column=6,
            end_column=11,
            start_pos=5,
            end_pos=10,
        ),
    )
    assert type_env.get("Langs") == lang_type
    assert type_env.get("lang") == lang_type
    assert type_env.get("langcode") == langtypes.STRING

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("lang") == EnumValue(ty="Langs", variant="English")
    assert env.get("langcode") == "eng"


@docstring_source_with_snapshot
def test_tuple_enum_def(source: str, snapshot: Any):
    """
    enum MaybeInt {
        Some(int)
        None
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get("MaybeInt") == Enum(
        enum_name="MaybeInt",
        members=["Some", "None"],
        span=Span(
            start_line=1,
            end_line=1,
            start_column=6,
            end_column=14,
            start_pos=5,
            end_pos=13,
        ),
    )

