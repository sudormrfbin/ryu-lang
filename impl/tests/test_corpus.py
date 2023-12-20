import pytest
from glob import glob

from tests.parser import TestSuite
from tests.sexp import parse_sexp

from compiler.parser import parse, parse_tree_to_ast
from compiler.typecheck import type_check


def get_suites(dir: str) -> list[TestSuite]:
    files = glob(f"{dir}/*.scm")

    suite = []

    for file in files:
        with open(file, "r") as f:
            sexp = parse_sexp(f.read())
            suite.append(TestSuite.from_sexp(sexp))

    assert suite, "Suite is empty, tests not discovered"

    return suite


TEST_SUITES = get_suites("tests/corpus")


@pytest.mark.parametrize("suite", TEST_SUITES)
def test_untyped_ast(suite: TestSuite):
    for case in suite.cases:
        if not case.untyped_ast_sexp:
            continue

        tree = parse(case.program)
        ast = parse_tree_to_ast(tree)

        assert ast.to_untyped_sexp() == case.untyped_ast_sexp


@pytest.mark.parametrize("suite", TEST_SUITES)
def test_typed_ast(suite: TestSuite):
    for case in suite.cases:
        if not case.typed_ast_sexp:
            continue

        tree = parse(case.program)
        ast = parse_tree_to_ast(tree)
        ast = type_check(ast)

        assert ast.to_typed_sexp() == case.typed_ast_sexp
