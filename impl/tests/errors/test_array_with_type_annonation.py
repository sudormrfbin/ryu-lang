import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import get_default_environs, run
from compiler.errors import ArrayTypeMismatch
from compiler.langtypes import BOOL, INT
from compiler.parser import parse, parse_tree_to_ast

EMPTY_TYPE_ENV, EMPTY_ENV = get_default_environs()


def test_array_with_type_annotation():
    with pytest.raises(ArrayTypeMismatch) as excinfo:
        ast = parse_tree_to_ast(parse("let x = <int>[true]"))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((1, 15), (1, 19))
    assert err.expected_type_span.coord() == ((1, 10), (1, 13))
    assert err.expected_type == INT
    assert err.actual_type == BOOL


def test_array_with_type_annotation_output(capfd: CaptureFixture[str], snapshot: str):
    run("let x = <int>[true]", EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
