from tests.sexp import LispAst


class TestCase:
    __test__ = False

    LISP_COMMAND_NAME = "test-case"

    def __init__(self, test_name: str, program: str):
        self.test_name = test_name
        self.program = program

        self.untyped_ast_sexp: LispAst | None = None
        self.typed_ast_sexp: LispAst | None = None

    @classmethod
    def from_sexp(cls, sexp: list[LispAst]):
        cmd_name = sexp.pop(0)
        assert cmd_name == cls.LISP_COMMAND_NAME, (
            f"Test cases must start with '{cls.LISP_COMMAND_NAME}', "
            f"got {cmd_name} instead"
        )

        case_name = sexp.pop(0)
        assert isinstance(
            case_name, str
        ), f"Test case name must be a string, got {case_name} instead"

        assert sexp.pop(0) == ":"
        arg = sexp.pop(0)
        assert arg == "program", f":program required as first argument, got '{arg}'"

        program = sexp.pop(0)

        testcase = cls(case_name, program)

        while sexp:
            match sexp.pop(0), sexp.pop(0):
                case ":", "untyped-ast":
                    testcase.untyped_ast_sexp = sexp.pop(0)
                case ":", "typed-ast":
                    testcase.typed_ast_sexp = sexp.pop(0)
                case unknown:
                    raise AttributeError(f"Unknown argument {unknown}")

        return testcase


class TestSuite:
    __test__ = False

    LISP_COMMAND_NAME = "test-suite"

    def __init__(self, suite_name: str, cases: list[TestCase]):
        self.suite_name = suite_name
        self.cases = cases

    @classmethod
    def from_sexp(cls, sexp: list[LispAst]):
        assert sexp[0] == cls.LISP_COMMAND_NAME, (
            f"Test suites must start with '{cls.LISP_COMMAND_NAME}', "
            f"got {sexp[0]} instead"
        )

        suite_name = sexp[1]
        assert isinstance(
            suite_name, str
        ), f"Suite name must be a string, got {suite_name} instead"

        cases = sexp[2:]
        cases = [TestCase.from_sexp(case) for case in cases]

        return cls(suite_name, cases)
