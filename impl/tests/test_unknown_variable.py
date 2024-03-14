import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import UnknownVariable
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()


def test_only_variable():
    with pytest.raises(UnknownVariable) as excinfo:
        ast = parse_tree_to_ast(parse("x"))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((1, 1), (1, 2))
    assert err.variable == "x"


def test_only_variable_output(capfd: CaptureFixture[str], snapshot: str):
    run("x", EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err


def test_variable_in_expr():
    with pytest.raises(UnknownVariable) as excinfo:
        ast = parse_tree_to_ast(parse("var+1"))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((1, 1), (1, 4))
    assert err.variable == "var"


def test_variable_in_expr_output(capfd: CaptureFixture[str], snapshot: str):
    run("var+1", EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
