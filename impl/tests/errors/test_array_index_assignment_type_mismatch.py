import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import ArrayIndexAssignmentTypeMismatch
from compiler.langtypes import BOOL, INT
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()


def test_if_stmt_not_bool_cond():
    with pytest.raises(ArrayIndexAssignmentTypeMismatch) as excinfo:
        ast = parse_tree_to_ast(
            parse(
                """let a=[1,3,5]
                                         a[2]=true"""
            )
        )
        ast.typecheck(EMPTY_TYPE_ENV)
        ast.eval(EMPTY_ENV)

    err = excinfo.value

    assert err.span.coord() == ((2, 47), (2, 51))


def test_only_variable_output(capfd: CaptureFixture[str], snapshot: str):
    run(
        """let a=[1,3,5]
           a[2]=true""",
        EMPTY_TYPE_ENV,
        EMPTY_ENV,
    )
    _, err = capfd.readouterr()
    assert snapshot == err
