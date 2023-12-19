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
        sexp = case.untyped_ast_sexp

        node = sexp[0]
        assert type(ast).__name__ == node, "Mismatched AST nodes"

        i = 1
        while i < len(sexp):
            match sexp[i]:
                case ":":
                    attr, val = sexp[i + 1], sexp[i + 2]
                    i += 3

                    assert type(attr) == str, "Attribute following : must be string"

                    assert hasattr(ast, attr), f"{node} node missing {attr} attribute"

                    attrvalue = getattr(ast, attr)
                    if isinstance(val, list):
                        assert_untyped_ast(val, attrvalue)
                    else:
                        assert val == str(attrvalue)


@pytest.mark.parametrize("suite", TEST_SUITES)
def test_typed_ast(suite: TestSuite):
    for case in suite.cases:
        if not case.typed_ast_sexp:
            continue

        tree = parse(case.program)
        ast = parse_tree_to_ast(tree)
        ast = type_check(ast)
        node = case.typed_ast_sexp[0]
        assert type(ast).__name__ == node, f"Mismatched AST nodes in '{case.test_name}'"

        match arg := case.typed_ast_sexp[1]:
            case str():
                assert (
                    type(ast._type).__name__ == arg
                ), f"Mismatched types in '{case.test_name}'"
            case _:
                assert False, "Unhandled case"
