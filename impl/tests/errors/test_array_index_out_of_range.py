import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import IndexingOutOfRange
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()

SOURCE = """\
let x=[1,2,3]
print x[3]
"""


def test_array_index_out_of_range():
    with pytest.raises(IndexingOutOfRange) as excinfo:
        ast = parse_tree_to_ast(parse(SOURCE))
        ast.typecheck(EMPTY_TYPE_ENV)
        ast.eval(EMPTY_ENV)

    err = excinfo.value

    assert err.span.coord() == ((2, 7), (2, 11))


def test_array_index_out_of_range_output(capfd: CaptureFixture[str], snapshot: str):
    run(SOURCE, EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
