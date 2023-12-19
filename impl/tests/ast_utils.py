from compiler.ast import _Ast
from tests.sexp import LispAst


def assert_untyped_ast(sexp: LispAst, ast: _Ast):
    node = sexp[0]
    assert type(ast).__name__ == node, "Mismatched AST nodes"

    i = 1
    while i < len(sexp):
        match sexp[i]:
            case ":":
                attr, val = sexp[i + 1], sexp[i + 2]
                i += 3

                assert type(attr) == str, "Attribute following : must be string"

                assert hasattr(ast, attr), f"{node} node missing {attr} attribute"

                attrvalue = getattr(ast, attr)
                if isinstance(val, list):
                    assert_untyped_ast(val, attrvalue)
                else:
                    assert val == str(attrvalue)
