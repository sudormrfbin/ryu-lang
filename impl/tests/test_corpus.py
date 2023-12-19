import pytest
from glob import glob

from tests.parser import TestSuite
from tests.sexp import parse_sexp
from tests.ast_utils import assert_untyped_ast

from compiler.parser import parse, parse_tree_to_ast


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
        if case.untyped_ast:
            tree = parse(case.program)
            ast = parse_tree_to_ast(tree)
            assert_untyped_ast(case.untyped_ast, ast)
