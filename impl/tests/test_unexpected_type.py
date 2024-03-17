import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import UnexpectedType
from compiler.langtypes import BOOL, INT
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()


def test_if_stmt_not_bool_cond():
    with pytest.raises(UnexpectedType) as excinfo:
        ast = parse_tree_to_ast(parse("if 13 { 34 }"))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((1, 4), (1, 6))
    assert err.expected_type == BOOL
    assert err.actual_type == INT


def test_only_variable_output(capfd: CaptureFixture[str], snapshot: str):
    run("if 13 { 34 }", EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
