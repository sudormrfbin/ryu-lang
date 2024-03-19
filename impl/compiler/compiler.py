from typing import TYPE_CHECKING, Any

# error_report submodule is generated dynamically by pyo3 on the rust
# side. Hence pyright cannot detect the source file.
from error_report.error_report import (  # pyright: ignore [reportMissingModuleSource]
    report_error,
)

from compiler.env import RuntimeEnvironment, TypeEnvironment

from . import errors
from .errors import (
    InvalidOperationError,
    OperandSpan,
    UndeclaredVariable,
    UnexpectedType,
    UnknownVariable,
)
from .parser import parse, parse_tree_to_ast

if TYPE_CHECKING:
    from error_report.error_report import (  # pyright: ignore [reportMissingModuleSource]
        Mark,
        Message,
    )


def run(source: str, type_env: TypeEnvironment, runtime_env: RuntimeEnvironment) -> Any:
    try:
        return _run(source, type_env, runtime_env)
    except errors.InvalidOperationError as err:
        handle_invalid_operation(err, source)
    except errors.UnknownVariable as err:
        handle_unknown_variable(err, source)
    except errors.UndeclaredVariable as err:
        handle_undeclared_variable(err, source)
    except errors.UnexpectedType as err:
        handle_unexpected_type(err, source)
    except errors.TypeMismatch as err:
        handle_type_mismatch(err, source)
    except errors.DuplicatedCase as err:
        handle_duplicated_case(err, source)
    except errors.InexhaustiveMatch as err:
        handle_inexhaustive_match(err, source)
    except errors.CompilerError as err:
        print(err)


def _run(
    source: str, type_env: TypeEnvironment, runtime_env: RuntimeEnvironment
) -> Any:
    tree = parse(source)
    ast = parse_tree_to_ast(tree)

    ast.typecheck(type_env)

    return ast.eval(runtime_env)


def handle_inexhaustive_match(err: errors.InexhaustiveMatch, source: str):
    expected_type_msg: Message = [
        "This is of type ",
        (err.expected_type.name, err.expected_type.name),
    ]
    expected_type_label: Mark = (
        expected_type_msg,
        err.expected_type.name,
        (err.expected_type_span.start_pos, err.expected_type_span.end_pos),
    )

    remaining = ", ".join((f"`{v}`" for v in err.remaining_values))
    add_block_msg: Message = [
        f"Add case block for value {remaining}"
        if len(err.remaining_values) == 1
        else f"Add case blocks for value {remaining}"
    ]
    add_block_label: Mark = (
        add_block_msg,
        (err.span.start_pos, err.span.end_pos),
    )

    labels: list[Mark] = [expected_type_label, add_block_label]
    message: Message = [
        "Match does not cover all cases for type ",
        (err.expected_type.name, err.expected_type.name),
    ]
    report_error(
        source=source,
        start_pos=err.span.start_pos,
        message=message,
        code=err.code,
        labels=labels,
    )


def handle_duplicated_case(err: errors.DuplicatedCase, source: str):
    first_occurance_msg: Message = [
        "This case is handled first here...",
    ]
    first_occurance_label: Mark = (
        first_occurance_msg,
        "color1",
        (err.previous_case_span.start_pos, err.previous_case_span.end_pos),
    )

    second_occurance_msg: Message = [
        "...and duplicated here",
    ]
    second_occurance_label: Mark = (
        second_occurance_msg,
        "color1",
        (err.span.start_pos, err.span.end_pos),
    )

    labels: list[Mark] = [first_occurance_label, second_occurance_label]
    message: Message = [
        "Duplicated case found in match expression",
    ]
    report_error(
        source=source,
        start_pos=err.span.start_pos,
        message=message,
        code=err.code,
        labels=labels,
    )


def handle_type_mismatch(err: errors.TypeMismatch, source: str):
    expected_type_msg: Message = [
        "Since this is of type ",
        (err.expected_type.name, err.expected_type.name),
        "...",
    ]
    expected_type_label: Mark = (
        expected_type_msg,
        err.expected_type.name,
        (err.expected_type_span.start_pos, err.expected_type_span.end_pos),
    )

    actual_type_msg: Message = [
        "...expected this to be ",
        (err.expected_type.name, err.expected_type.name),
        " too, but found ",
        (err.actual_type.name, err.actual_type.name),
    ]
    actual_type_label: Mark = (
        actual_type_msg,
        err.actual_type.name,
        (err.span.start_pos, err.span.end_pos),
    )

    labels: list[Mark] = [expected_type_label, actual_type_label]
    message: Message = [
        "Expected a type of ",
        (err.expected_type.name, err.expected_type.name),
        " but found ",
        (err.actual_type.name, err.actual_type.name),
    ]
    report_error(
        source=source,
        start_pos=err.span.start_pos,
        message=message,
        code=err.code,
        labels=labels,
    )


def handle_unexpected_type(err: UnexpectedType, source: str):
    actual_type_msg: Message = [
        "This is of type ",
        (err.actual_type.name, err.actual_type.name),
    ]
    actual_type_label: Mark = (
        actual_type_msg,
        err.actual_type.name,
        (err.span.start_pos, err.span.end_pos),
    )
    labels: list[Mark] = [actual_type_label]
    message: Message = [
        "Expected a type of ",
        (err.expected_type.name, err.expected_type.name),
        " but found ",
        (err.actual_type.name, err.actual_type.name),
    ]
    report_error(
        source=source,
        start_pos=err.span.start_pos,
        message=message,
        code=err.code,
        labels=labels,
    )


def handle_unknown_variable(err: UnknownVariable, source: str):
    labels: list[Mark] = [
        (["Not defined"], err.variable, (err.span.start_pos, err.span.end_pos)),
    ]
    message: Message = [
        "Variable ",
        (err.variable, err.variable),
        " not defined in this scope",
    ]
    report_error(
        source=source,
        start_pos=err.span.start_pos,
        message=message,
        code=err.code,
        labels=labels,
    )


def handle_undeclared_variable(err: UndeclaredVariable, source: str):
    labels: list[Mark] = [
        (["Not defined"], err.variable, (err.span.start_pos, err.span.end_pos)),
    ]
    message: Message = [
        "Variable ",
        (err.variable, err.variable),
        " not defined in this scope",
    ]
    report_error(
        source=source,
        start_pos=err.span.start_pos,
        message=message,
        code=err.code,
        labels=labels,
    )


def handle_invalid_operation(err: InvalidOperationError, source: str):
    labels: list[Mark] = []
    for op in err.operands:
        msg: Message = ["This is of type ", (op.type_.name, op.type_.name)]
        labels.append(
            (
                msg,
                op.type_.name,
                (op.span.start_pos, op.span.end_pos),
            )
        )

    operator = err.operator
    message: Message
    match err.operands:
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
            raise errors.InternalCompilerError("Unhandled case")

    report_error(
        source=source,
        start_pos=err.span.start_pos,
        message=message,
        code=err.code,
        labels=labels,
    )
