import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import IndexingNonArray
from compiler.langtypes import INT
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()

SOURCE_1 = """\
let x = 2
print x[2]
"""


def test_indexing_non_array():
    with pytest.raises(IndexingNonArray) as excinfo:
        ast = parse_tree_to_ast(parse(SOURCE_1))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((2, 7), (2, 8))


def test_indexing_non_array_output(capfd: CaptureFixture[str], snapshot: str):
    run(SOURCE_1, EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err


SOURCE_2 = """\
let x = 2
x[2] = 1
"""


def test_indexing_non_array_assignment():
    with pytest.raises(IndexingNonArray) as excinfo:
        ast = parse_tree_to_ast(parse(SOURCE_2))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((2, 1), (2, 2))
    assert err.actual_type == INT


def test_indexing_non_array_assignment_output(
    capfd: CaptureFixture[str], snapshot: str
):
    run(SOURCE_2, EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
