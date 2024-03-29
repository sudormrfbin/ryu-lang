import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import IndexingOutOfRange
from compiler.langtypes import BOOL, INT
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()


def test_if_stmt_not_bool_cond():
    with pytest.raises(IndexingOutOfRange) as excinfo:
        ast = parse_tree_to_ast(parse('''let x=[1,2,3]
                                         print x[3]'''))
        ast.typecheck(EMPTY_TYPE_ENV)
        ast.eval(EMPTY_ENV)

    err = excinfo.value

    assert err.span.coord() == ((2,48),(2,52))


def test_only_variable_output(capfd: CaptureFixture[str], snapshot: str):
    run('''let x=[1,2,3]
          print x[3]''', EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
