from abc import abstractmethod
from typing import ClassVar, Container
import dataclasses
from dataclasses import dataclass
from typing_extensions import override

from lark.tree import Meta
from lark.lexer import Token

from compiler import langtypes
from compiler import report

from compiler.report import Labels, Text, Label

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
        operator = self.operator
        description: Text
        match self.operands:
            case [OperandSpan(type_=t)]:
                description = Text(
                    f"Invalid operation '{operator.name}' for type ",
                    Text.colored(t.name),
                )
            case [OperandSpan(type_=t1), OperandSpan(type_=t2)]:
                description = Text(
                    f"Invalid operation '{operator.name}' for types ",
                    Text.colored(t1.name),
                    " and ",
                    Text.colored(t2.name),
                )
            case _:
                raise InternalCompilerError("Unhandled case")

        labels: Labels = []
        for op in self.operands:
            labels.append(
                Label.colored_text(
                    Text("This is of type ", Text.colored(op.type_.name)),
                    color_id=op.type_.name,
                    span=op.span,
                )
            )

        self._report(source, description, labels)


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
        description = Text(
            "Expected a type of ",
            Text.colored(self.expected_type.name),
            " but found ",
            Text.colored(self.actual_type.name),
        )

        labels = [
            Label.colored_text(
                Text("This is of type ", Text.colored(self.actual_type.name)),
                color_id=self.actual_type.name,
                span=self.span,
            )
        ]

        self._report(source, description, labels)


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
        description = Text(
            "Expected a type of ",
            Text.colored(self.expected_type.name),
            " but found ",
            Text.colored(self.actual_type.name),
        )

        expected_type_label = Label.colored_text(
            Text(
                "Since this is of type ",
                Text.colored(self.expected_type.name),
                "...",
            ),
            color_id=self.expected_type.name,
            span=self.expected_type_span,
        )

        actual_type_label = Label.colored_text(
            Text(
                "...expected this to be ",
                Text.colored(self.expected_type.name),
                " too, but found ",
                Text.colored(self.actual_type.name),
            ),
            color_id=self.actual_type.name,
            span=self.span,
        )

        labels = [expected_type_label, actual_type_label]

        self._report(source, description, labels)


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
        description = Text("Duplicated case found in match expression")

        first_occurance_label = Label.colored_text(
            Text("This case is handled first here..."),
            color_id="color1",
            span=self.previous_case_span,
        )

        second_occurance_label = Label.colored_text(
            Text("...and duplicated here"),
            color_id="color1",
            span=self.span,
        )

        labels = [first_occurance_label, second_occurance_label]

        self._report(source, description, labels)


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
        description = Text(
            "Match does not cover all cases for type ",
            Text.colored(self.expected_type.name),
        )

        expected_type_label = Label.colored_text(
            Text(
                "This is of type ",
                Text.colored(self.expected_type.name),
            ),
            color_id=self.expected_type.name,
            span=self.expected_type_span,
        )

        remaining = ", ".join((f"`{v}`" for v in self.remaining_values))
        add_block_msg = Text(
            f"Add case block for value {remaining}"
            if len(self.remaining_values) == 1
            else f"Add case blocks for value {remaining}"
        )
        add_block_label = Label.text(
            add_block_msg,
            span=self.span,
        )

        labels = [expected_type_label, add_block_label]

        self._report(source, description, labels)


@dataclass
class ArrayTypeMismatch(CompilerError):
    code = 8

    expected_type: langtypes.Type
    actual_type: langtypes.Type
    expected_type_span: Span

    @override
    def report(self, source: str):
        description = Text(
            "Expected a type of ",
            Text.colored(self.expected_type.name),
            " but found ",
            Text.colored(self.actual_type.name),
            ", Array elements need to be of same datatype",
        )

        labels = [
            Label.colored_text(
                Text("This is of type ", Text.colored(self.actual_type.name)),
                color_id=self.actual_type.name,
                span=self.span,
            ),
            Label.colored_text(
                Text("This is of type ", Text.colored(self.expected_type.name)),
                color_id=self.expected_type.name,
                span=self.expected_type_span,
            ),
        ]

        self._report(source, description, labels)


@dataclass
class EmptyArrayWithoutTypeAnnotation(CompilerError):
    """
    Raised when a array declared without type annonation
    let x=[]

    FIX
    let x = <int>[]
    """

    code = 9

    @override
    def report(self, source: str):
        description = Text(
            "Empty array cannot be declared without specifying data type",
        )

        labels = [
            Label.colored_text(
                Text("<", Text.colored("data type"), ">[]"),
                color_id="data type",
                span=self.span,
            )
        ]

        self._report(source, description, labels)


@dataclass
class IndexingNonArray(CompilerError):
    """
    Raised when a index used on non-array data type
    let x=2
    x[1]

    """

    code = 11
    actual_type: langtypes.Type

    @override
    def report(self, source: str):
        description = Text(
            " Expression needs to be of ",
            Text.colored("Array"),
            " data type to use indexing operations ",
        )

        labels = [
            Label.colored_text(
                Text("is of ", Text.colored(self.actual_type.name)),
                color_id=self.actual_type.name,
                span=self.span,
            )
        ]

        self._report(source, description, labels)


@dataclass
class IndexingOutOfRange(CompilerError):
    """
    Raised when a index out of bound
    let x=[1,2,3]
    print x[3]

    """

    code = 13

    length_array: int
    index_value: int

    @override
    def report(self, source: str):
        description = Text(
            "Indexing is out of range, ",
            " maximum range is ",
            Text.colored(str(self.length_array - 1)),
            " but used value is :",
            Text.colored(str(self.index_value)),
        )

        labels = [
            Label.colored_text(
                Text("is out of range "),
                color_id=" ",
                span=self.span,
            )
        ]
        self._report(source, description, labels)


@dataclass
class ArrayIndexAssignmentTypeMismatch(CompilerError):
    code = 14

    actual_type: langtypes.Type
    expected_type: langtypes.Type
    expected_array_type: langtypes.Type
    expected_type_span: Span

    @override
    def report(self, source: str):
        description = Text(
            "Expected a type of ",
            Text.colored(self.expected_array_type.name),
            " but found ",
            Text.colored(self.actual_type.name),
        )

        expected_type_label = Label.colored_text(
            Text(
                "Since this is of type ",
                Text.colored(self.expected_type.name),
                "...",
            ),
            color_id=self.expected_type.name,
            span=self.expected_type_span,
        )

        actual_type_label = Label.colored_text(
            Text(
                "...expected this to be ",
                Text.colored(self.expected_array_type.name),
                ", but found ",
                Text.colored(self.actual_type.name),
            ),
            color_id=self.actual_type.name,
            span=self.span,
        )

        labels = [expected_type_label, actual_type_label]

        self._report(source, description, labels)
