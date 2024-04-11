import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import InexhaustiveMatch
from compiler.parser import parse, parse_tree_to_ast
from tests.utils import multiline_sanitize

SOURCE = multiline_sanitize(
    """
enum MaybeBool {
    Some(bool)
    None
}

match MaybeBool::None {
    case MaybeBool::Some(true) { 1 }
    case MaybeBool::None { 2 }
}
"""
)


def test_match_tuple_inexhaustive_match():
    with pytest.raises(InexhaustiveMatch) as excinfo:
        ast = parse_tree_to_ast(parse(SOURCE))
        ast.typecheck(TypeEnvironment())

    err = excinfo.value

    assert err.span.coord() == ((6, 1), (9, 2))
    assert err.remaining_values == {"MaybeBool::Some(False)"}


def test_match_tuple_inexhaustive_match_output(
    capfd: CaptureFixture[str], snapshot: str
):
    run(SOURCE, TypeEnvironment(), RuntimeEnvironment())
    _, err = capfd.readouterr()
    assert snapshot == err
