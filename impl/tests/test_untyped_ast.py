from ast_utils import assert_untyped_ast
from sexp import parse_sexp


def test_boolliteral():
    from compiler.ast import BoolLiteral

    bl = BoolLiteral(value=True)
    inp = "(BoolLiteral :value True)"
    assert_untyped_ast(parse_sexp(inp), bl)
