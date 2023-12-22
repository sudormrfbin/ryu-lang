import pytest
from glob import glob

from tests.parser import TestSuite, TestCase
from tests.sexp import parse_sexp

from compiler.parser import parse, parse_tree_to_ast
from compiler.errors import CompilerError


def get_suites(dir: str) -> list[TestSuite]:
    files = glob(f"{dir}/*.scm")

    suite = []

    for file in files:
        with open(file, "r") as f:
            sexp = parse_sexp(f.read())
            suite.append(TestSuite.from_sexp(sexp))

    assert suite, "Suite is empty, tests not discovered"

    return suite


def get_cases(suites: list[TestSuite]) -> list[TestCase]:
    return sum((s.cases for s in suites), start=[])


TEST_SUITES = get_suites("tests/corpus")
TEST_CASES = get_cases(TEST_SUITES)


def case_id(val):
    if isinstance(val, TestCase):
        return val.test_name


@pytest.mark.parametrize(
    "case",
    [c for c in TEST_CASES if c.untyped_ast_sexp],
    ids=case_id,
)
def test_untyped_ast(case: TestCase):
    tree = parse(case.program)
    ast = parse_tree_to_ast(tree)

    assert ast.to_untyped_sexp() == case.untyped_ast_sexp


@pytest.mark.parametrize(
    "case",
    [c for c in TEST_CASES if c.typed_ast_sexp],
    ids=case_id,
)
def test_typed_ast(case: TestCase):
    tree = parse(case.program)
    ast = parse_tree_to_ast(tree)
    ast.typecheck()

    assert ast.to_typed_sexp() == case.typed_ast_sexp


@pytest.mark.parametrize(
    "case",
    [c for c in TEST_CASES if c.eval],
    ids=case_id,
)
def test_eval(case: TestCase):
    tree = parse(case.program)
    ast = parse_tree_to_ast(tree)
    ast.typecheck()

    assert str(ast.eval()) == case.eval


@pytest.mark.parametrize(
    "case",
    [c for c in TEST_CASES if c.error],
    ids=case_id,
)
def test_error(case: TestCase):
    with pytest.raises(CompilerError) as excinfo:
        tree = parse(case.program)
        ast = parse_tree_to_ast(tree)
        ast.typecheck()

    assert excinfo.value.to_sexp() == case.error
