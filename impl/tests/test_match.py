from typing import Any
from compiler.compiler import get_default_environs
from compiler.parser import parse, parse_tree_to_ast
from compiler.langtypes import INT
from tests.utils import docstring_source_with_snapshot


@docstring_source_with_snapshot
def test_match_case_bool(source: str, snapshot: Any):
    """
    let result = -1

    match true {
        case true { result = 1 }
        case false { result = 0 }
    }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot

    type_env, env = get_default_environs()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot

    assert type_env.get_var_type("result") == INT

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

    type_env, env = get_default_environs()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot(name="typed-ast")

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

    type_env, env = get_default_environs()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot(name="typed-ast")

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

    type_env, env = get_default_environs()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot(name="typed-ast")

    ast.eval(env)
    assert env.get("zero") == 0
    assert env.get("one") == -1
    assert env.get("two") == -1
    assert env.get("three") == -1
    assert env.get("more") == -1


@docstring_source_with_snapshot
def test_match_array_wildcard_element(source: str, snapshot: Any):
    """
    fn contains_one(arr: array<int>) -> bool {
        match arr {
            case [1, _, _] { return true }
            case [_, 1, _] { return true }
            case [_, _, 1] { return true }
            case _ { return false }
        }
    }

    let no = contains_one(<int>[])
    let one = contains_one([1, 2, 3])
    let two = contains_one([3, 1, 2])
    let three = contains_one([2, 3, 1])
    let no2 = contains_one([2, 3, 3])
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot(name="ast")

    type_env, env = get_default_environs()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot(name="typed-ast")

    ast.eval(env)
    assert env.get("no") is False
    assert env.get("one") is True
    assert env.get("two") is True
    assert env.get("three") is True
    assert env.get("no2") is False
