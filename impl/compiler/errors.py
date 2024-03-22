from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar, Container
import dataclasses
from dataclasses import dataclass
from typing_extensions import override

from lark.tree import Meta
from lark.lexer import Token

from compiler import langtypes
from compiler import report

from compiler.report import Text, Label

# error_report submodule is generated dynamically by pyo3 on the rust
# side. Hence pyright cannot detect the source file.
from error_report.error_report import (  # pyright: ignore [reportMissingModuleSource]
    report_error,
)

if TYPE_CHECKING:
    from error_report.error_report import (  # pyright: ignore [reportMissingModuleSource]
        Mark,
        Message,
    )

LineCol = tuple[int, int]


@dataclass
class Span:
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    start_pos: int
    end_pos: int

    def pos(self) -> tuple[int, int]:
        return (self.start_pos, self.end_pos)

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

    def _report(self, source: str, description: report.Text, labels: report.Labels):
        report.report_error(
            source=source,
            start_pos=self.span.start_pos,
            description=description,
            code=self.code,
            labels=labels,
        )

    @abstractmethod
    def report(self, source: str):
        print(self)


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

    @override
    def report(self, source: str):
        labels: list[Mark] = []
        for op in self.operands:
            msg: Message = ["This is of type ", (op.type_.name, op.type_.name)]
            labels.append(
                (
                    msg,
                    op.type_.name,
                    (op.span.start_pos, op.span.end_pos),
                )
            )

        operator = self.operator
        message: Message
        match self.operands:
            case [OperandSpan(type_=t)]:
                message = [
                    f"Invalid operation '{operator.name}' for type ",
                    (t.name, t.name),
                ]
            case [OperandSpan(type_=t1), OperandSpan(type_=t2)]:
                message = [
                    f"Invalid operation '{operator.name}' for types ",
                    (t1.name, t1.name),
                    " and ",
                    (t2.name, t2.name),
                ]
            case _:
                raise InternalCompilerError("Unhandled case")

        report_error(
            source=source,
            start_pos=self.span.start_pos,
            message=message,
            code=self.code,
            labels=labels,
        )


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

    @override
    def report(self, source: str):
        description = Text(
            "Variable ",
            Text.colored(self.variable),
            " not defined in this scope",
        )
        labels = [
            Label.colored_text(
                Text("Not defined"), color_id=self.variable, span=self.span
            )
        ]

        self._report(source, description, labels)


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

    @override
    def report(self, source: str):
        description = Text(
            "Variable ",
            Text.colored(self.variable),
            " not defined in this scope",
        )
        labels = [
            Label.colored_text(
                Text("Not defined"),
                color_id=self.variable,
                span=self.span,
            ),
        ]
        self._report(source, description, labels)


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

    @override
    def report(self, source: str):
        actual_type_msg: Message = [
            "This is of type ",
            (self.actual_type.name, self.actual_type.name),
        ]
        actual_type_label: Mark = (
            actual_type_msg,
            self.actual_type.name,
            (self.span.start_pos, self.span.end_pos),
        )
        labels: list[Mark] = [actual_type_label]
        message: Message = [
            "Expected a type of ",
            (self.expected_type.name, self.expected_type.name),
            " but found ",
            (self.actual_type.name, self.actual_type.name),
        ]
        report_error(
            source=source,
            start_pos=self.span.start_pos,
            message=message,
            code=self.code,
            labels=labels,
        )


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

    @override
    def report(self, source: str):
        expected_type_msg: Message = [
            "Since this is of type ",
            (self.expected_type.name, self.expected_type.name),
            "...",
        ]
        expected_type_label: Mark = (
            expected_type_msg,
            self.expected_type.name,
            (self.expected_type_span.start_pos, self.expected_type_span.end_pos),
        )

        actual_type_msg: Message = [
            "...expected this to be ",
            (self.expected_type.name, self.expected_type.name),
            " too, but found ",
            (self.actual_type.name, self.actual_type.name),
        ]
        actual_type_label: Mark = (
            actual_type_msg,
            self.actual_type.name,
            (self.span.start_pos, self.span.end_pos),
        )

        labels: list[Mark] = [expected_type_label, actual_type_label]
        message: Message = [
            "Expected a type of ",
            (self.expected_type.name, self.expected_type.name),
            " but found ",
            (self.actual_type.name, self.actual_type.name),
        ]
        report_error(
            source=source,
            start_pos=self.span.start_pos,
            message=message,
            code=self.code,
            labels=labels,
        )


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

    @override
    def report(self, source: str):
        first_occurance_msg: Message = [
            "This case is handled first here...",
        ]
        first_occurance_label: Mark = (
            first_occurance_msg,
            "color1",
            (self.previous_case_span.start_pos, self.previous_case_span.end_pos),
        )

        second_occurance_msg: Message = [
            "...and duplicated here",
        ]
        second_occurance_label: Mark = (
            second_occurance_msg,
            "color1",
            (self.span.start_pos, self.span.end_pos),
        )

        labels: list[Mark] = [first_occurance_label, second_occurance_label]
        message: Message = [
            "Duplicated case found in match expression",
        ]
        report_error(
            source=source,
            start_pos=self.span.start_pos,
            message=message,
            code=self.code,
            labels=labels,
        )


@dataclass
class InexhaustiveMatch(CompilerError):
    """
    Raised when a match statement is not exhaustive.

    ## Example
    ```
    match true {
        case true {}
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

    code = 7

    expected_type: langtypes.Type
    expected_type_span: Span
    remaining_values: Container[bool | str]

    @override
    def report(self, source: str):
        expected_type_msg: Message = [
            "This is of type ",
            (self.expected_type.name, self.expected_type.name),
        ]
        expected_type_label: Mark = (
            expected_type_msg,
            self.expected_type.name,
            (self.expected_type_span.start_pos, self.expected_type_span.end_pos),
        )

        remaining = ", ".join((f"`{v}`" for v in self.remaining_values))
        add_block_msg: Message = [
            f"Add case block for value {remaining}"
            if len(self.remaining_values) == 1
            else f"Add case blocks for value {remaining}"
        ]
        add_block_label: Mark = (
            add_block_msg,
            (self.span.start_pos, self.span.end_pos),
        )

        labels: list[Mark] = [expected_type_label, add_block_label]
        message: Message = [
            "Match does not cover all cases for type ",
            (self.expected_type.name, self.expected_type.name),
        ]
        report_error(
            source=source,
            start_pos=self.span.start_pos,
            message=message,
            code=self.code,
            labels=labels,
        )
