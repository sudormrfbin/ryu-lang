from typing import ClassVar
import dataclasses
from dataclasses import dataclass
from typing_extensions import override

from lark.tree import Meta
from lark.lexer import Token

from compiler import langtypes

LineCol = tuple[int, int]


@dataclass
class Span:
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    start_pos: int
    end_pos: int

    @classmethod
    def from_meta(cls, meta: Meta) -> "Span":
        return cls(
            start_line=meta.line,
            end_line=meta.end_line,
            start_column=meta.column,
            end_column=meta.end_column,
            start_pos=meta.start_pos,
            end_pos=meta.end_pos,
        )

    @classmethod
    def from_token(cls, token: Token) -> "Span":
        assert token.line is not None
        assert token.end_line is not None
        assert token.column is not None
        assert token.end_column is not None
        assert token.start_pos is not None
        assert token.end_pos is not None

        return cls(
            start_line=token.line,
            end_line=token.end_line,
            start_column=token.column,
            end_column=token.end_column,
            start_pos=token.start_pos,
            end_pos=token.end_pos,
        )

    def coord(self) -> tuple[LineCol, LineCol]:
        start = (self.start_line, self.start_column)
        end = (self.end_line, self.end_column)
        return (start, end)


class InternalCompilerError(Exception):
    pass


@dataclass
class CompilerError(Exception):
    code: ClassVar[int]

    message: str
    span: Span

    def __post_init__(self):
        attributes = dataclasses.astuple(self)
        # Custom exceptions must always call super(), we use the __post_init__
        # mechanism provided by dataclasses to call the super constructor after
        # this class's __init__ is called.
        super().__init__(*attributes)

    @override
    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.message}"


@dataclass
class OperatorSpan:
    name: str
    span: Span


@dataclass
class OperandSpan:
    type_: langtypes.Type
    span: Span


@dataclass
class InvalidOperationError(CompilerError):
    code = 1

    operator: OperatorSpan
    operands: list[OperandSpan]


@dataclass
class UnknownVariable(CompilerError):
    """
    Raised when a variable is used in an expression without declaring it prior.

    ## Example
    ```
    print(var + 5)
    ```
    """

    code = 2

    variable: str


@dataclass
class UndeclaredVariable(CompilerError):
    """
    Raised when the lvalue (the variable part) of an assignment has not
    been declared prior to assignment.

    ## Example
    ```
    var = 4
    ```

    ## Fix
    ```
    let var = 4
    ```
    """

    code = 3

    variable: str


@dataclass
class UnexpectedType(CompilerError):
    """
    Raised when an expression deviates from it's expected type.

    ## Example
    ```
    if 1 {}
    ```

    ## Fix
    ```
    if true {}
    ```
    """

    code = 4

    expected_type: langtypes.Type
    actual_type: langtypes.Type


@dataclass
class TypeMismatch(CompilerError):
    """
    Raised when an expression is expected to be of a particular type
    because of a declaration in another point in the source code.

    ## Example
    ```
    match true {
        case 1 {}
        case 2 {}
    }
    ```

    ## Fix
    ```
    match 1 {
        case 1 {}
        case 2 {}
    }
    ```
    """

    code = 5

    actual_type: langtypes.Type
    expected_type: langtypes.Type
    expected_type_span: Span


@dataclass
class DuplicatedCase(CompilerError):
    """
    Raised when a match statement has duplicated case arms.

    ## Example
    ```
    match true {
        case true {}
        case false {}
    }
    ```

    ## Fix
    ```
    match true {
        case true {}
        case false {}
    }
    ```
    """

    code = 6

    previous_case_span: Span
