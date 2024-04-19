from typing import Any
from compiler import langtypes
from compiler.compiler import get_default_environs
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import Span
from compiler.langtypes import BOOL, INT, Enum
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

    assert type_env.get_type("Langs") == Enum(
        enum_name="Langs",
        members=[
            Enum.Simple("Malayalam"),
            Enum.Simple("English"),
            Enum.Simple("Japanese"),
        ],
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
        members=[
            Enum.Simple("Malayalam"),
            Enum.Simple("English"),
            Enum.Simple("Japanese"),
        ],
        span=Span(
            start_line=1,
            end_line=1,
            start_column=6,
            end_column=11,
            start_pos=5,
            end_pos=10,
        ),
    )
    assert type_env.get_type("Langs") == lang_type
    assert type_env.get_var_type("lang") == lang_type

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
        members=[
            Enum.Simple("Malayalam"),
            Enum.Simple("English"),
            Enum.Simple("Japanese"),
        ],
        span=Span(
            start_line=1,
            end_line=1,
            start_column=6,
            end_column=11,
            start_pos=5,
            end_pos=10,
        ),
    )
    assert type_env.get_type("Langs") == lang_type
    assert type_env.get_var_type("lang") == lang_type
    assert type_env.get_var_type("langcode") == langtypes.STRING

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

    type_env, _ = get_default_environs()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get_type("MaybeInt") == Enum(
        enum_name="MaybeInt",
        members=[Enum.Tuple("Some", INT), Enum.Simple("None")],
        span=Span(
            start_line=1,
            end_line=1,
            start_column=6,
            end_column=14,
            start_pos=5,
            end_pos=13,
        ),
    )


@docstring_source_with_snapshot
def test_tuple_enum_assignment(source: str, snapshot: Any):
    """
    enum MaybeInt {
        Some(int)
        None
    }

    let x = MaybeInt::Some(8)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env, env = get_default_environs()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    enum_type = Enum(
        enum_name="MaybeInt",
        members=[Enum.Tuple("Some", INT), Enum.Simple("None")],
        span=Span(
            start_line=1,
            end_line=1,
            start_column=6,
            end_column=14,
            start_pos=5,
            end_pos=13,
        ),
    )

    assert type_env.get_type("MaybeInt") == enum_type
    assert type_env.get_var_type("x") == enum_type

    ast.eval(env)


@docstring_source_with_snapshot
def test_tuple_enum_match(source: str, snapshot: Any):
    """
    enum MaybeBool {
        Some(bool)
        None
    }

    fn eval(v: MaybeBool) -> int {
        match v {
            case MaybeBool::Some(true) { return 0 }
            case MaybeBool::Some(false) { return 1 }
            case MaybeBool::None { return 2 }
        }
    }

    let zero = eval(MaybeBool::Some(true))
    let one = eval(MaybeBool::Some(false))
    let two = eval(MaybeBool::None)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env, env = get_default_environs()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    enum_type = Enum(
        enum_name="MaybeBool",
        members=[Enum.Tuple("Some", BOOL), Enum.Simple("None")],
        span=Span(
            start_line=1,
            end_line=1,
            start_column=6,
            end_column=15,
            start_pos=5,
            end_pos=14,
        ),
    )

    assert type_env.get_type("MaybeBool") == enum_type

    ast.eval(env)

    assert env.get("zero") == 0
    assert env.get("one") == 1
    assert env.get("two") == 2


# @docstring_source_with_snapshot
# def test_enum_with_generics(source: str, snapshot: Any):
#     """
#     enum Option<T> {
#         Some(T)
#         None
#     }

#     enum Result<T, E> {
#         Ok(T),
#         Err(E)
#     }
#     """
#     ast = parse_tree_to_ast(parse(source))
#     assert ast.to_dict() == snapshot

#     type_env = TypeEnvironment()
#     ast.typecheck(type_env)
#     assert ast.to_type_dict() == snapshot

#     assert type_env.get("Option") == Enum(
#         enum_name="Option",
#         members=["Some", "None"],
#         span=Span(
#             start_line=1,
#             end_line=1,
#             start_column=6,
#             end_column=11,
#             start_pos=5,
#             end_pos=10,
#         ),
#     )
