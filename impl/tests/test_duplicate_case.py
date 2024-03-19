import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import DuplicatedCase, UnexpectedType
from compiler.langtypes import BOOL, INT
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
    case true {
        2
    }
}
"""
)


def test_match_duplicated_case():
    with pytest.raises(DuplicatedCase) as excinfo:
        ast = parse_tree_to_ast(parse(SOURCE))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((5, 10), (5, 14))
    assert err.previous_case_span.coord() == ((2, 10), (2, 14))


def test_only_variable_output(capfd: CaptureFixture[str], snapshot: str):
    run(SOURCE, EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
