import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import UnexpectedType
from compiler.langtypes import Array, INT
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()


def test_for_stmt_non_array_cond():
    with pytest.raises(UnexpectedType) as excinfo:
        ast = parse_tree_to_ast(parse("for i in 43 { print i }"))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((1, 10), (1, 12))
    assert err.expected_type == Array(err.actual_type)
    assert err.actual_type == INT


def test_for_stmt_output(capfd: CaptureFixture[str], snapshot: str):
    run("for i in 43 { print i }", EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
