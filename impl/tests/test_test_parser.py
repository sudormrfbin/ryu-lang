from tests.sexp import parse_sexp
from tests.parser import TestSuite


def test_parser():
    inp = """(test-suite "literals"

  (test-case "true literal"
   :program
     "true"
   :untyped-ast
     (BoolLiteral :value True)
   :typed-ast
     (BoolLiteral Boolean)))
"""

    suite = TestSuite.from_sexp(parse_sexp(inp))

    assert suite.suite_name == "literals"

    case = suite.cases[0]

    assert case.test_name == "true literal"
    assert case.program == "true"
    assert case.untyped_ast == ["BoolLiteral", ":", "value", "True"]
    assert case.typed_ast == ["BoolLiteral", "Boolean"]
