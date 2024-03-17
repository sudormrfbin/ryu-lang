import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import UndeclaredVariable
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()


def test_undeclared_assignment():
    with pytest.raises(UndeclaredVariable) as excinfo:
        ast = parse_tree_to_ast(parse("x=2"))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((1, 1), (1, 2))
    assert err.variable == "x"


def test_undeclared_assignment_output(capfd: CaptureFixture[str], snapshot: str):
    run("x=2", EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
