import pytest

from compiler.parser import parse, parse_tree_to_ast
from compiler.errors import OperandSpan, InvalidOperationError


def test_unary_op_bool_error():
    with pytest.raises(InvalidOperationError) as excinfo:
        ast = parse_tree_to_ast(parse("-true"))
        ast.typecheck()

    err = excinfo.value

    assert err.span.coord() == ((1, 1), (1, 6))
    assert err.operator.name == "-"
    assert err.operator.span.coord() == ((1, 1), (1, 2))

    match err.operands:
        case [OperandSpan(type_=type_, span=span)]:
            assert type_.name == "Bool"
            assert span.coord() == ((1, 2), (1, 6))
        case _:
            assert False
