import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import InexhaustiveMatch
from compiler.parser import parse, parse_tree_to_ast
from tests.utils import multiline_sanitize

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()


SOURCE = multiline_sanitize(
    """
match true {
    case true {
        1
    }
}
"""
)


def test_match_inexhaustive_match():
    with pytest.raises(InexhaustiveMatch) as excinfo:
        ast = parse_tree_to_ast(parse(SOURCE))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((1, 1), (5, 2))
    assert err.remaining_values == {False}


def test_only_variable_output(capfd: CaptureFixture[str], snapshot: str):
    run(SOURCE, EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
