from typing import Any
from compiler import langtypes, langvalues
from compiler.compiler import get_default_environs
from compiler.parser import parse, parse_tree_to_ast
from tests.utils import docstring_source_with_snapshot


@docstring_source_with_snapshot
def test_match_array_empty_case(source: str, snapshot: Any):
    """
    let i = sum(2, 3)
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == snapshot(name="ast")

    type_env, runtime_env = get_default_environs()

    ast.typecheck(type_env)
    assert ast.to_type_dict() == snapshot(name="typed-ast")
    assert isinstance(type_env.get_var_type("sum"), langtypes.Function)

    ast.eval(runtime_env)
    assert isinstance(runtime_env.get("sum"), langvalues.BuiltinFunction)
    assert runtime_env.get("i") == 5
