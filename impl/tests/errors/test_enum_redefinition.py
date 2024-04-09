import pytest
from _pytest.capture import CaptureFixture

from compiler.compiler import run
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.errors import TypeRedefinition
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()

SOURCE = """\
enum Lang {
    Eng
}

enum Lang {
    Urdu
}
"""


def test_enum_redefinition():
    with pytest.raises(TypeRedefinition) as excinfo:
        ast = parse_tree_to_ast(parse(SOURCE))
        ast.typecheck(EMPTY_TYPE_ENV)

    err = excinfo.value

    assert err.span.coord() == ((5, 6), (5, 10))
    assert err.type_name == "Lang"
    assert err.previous_type_span.coord() == ((1, 6), (1, 10))


def test_enum_redefinition_output(capfd: CaptureFixture[str], snapshot: str):
    run(SOURCE, EMPTY_TYPE_ENV, EMPTY_ENV)
    _, err = capfd.readouterr()
    assert snapshot == err
