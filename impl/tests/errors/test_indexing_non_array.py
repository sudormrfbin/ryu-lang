import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import IndexingNonArray
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()

SOURCE = """\
let x = 2
print x[2]
"""


def test_indexing_non_array():
    with pytest.raises(IndexingNonArray) as excinfo:
        ast = parse_tree_to_ast(parse(SOURCE))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((2, 7), (2, 8))


def test_indexing_non_array_output(capfd: CaptureFixture[str], snapshot: str):
    run(SOURCE, EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
