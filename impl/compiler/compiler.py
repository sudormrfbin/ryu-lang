from typing import TYPE_CHECKING, Any

# error_report submodule is generated dynamically by pyo3 on the rust
# side. Hence pyright cannot detect the source file.
from error_report.error_report import (  # pyright: ignore [reportMissingModuleSource]
    report_error,
)

from compiler.env import RuntimeEnvironment, TypeEnvironment

from compiler import errors
from compiler.errors import (
    InvalidOperationError,
    OperandSpan,
    UndeclaredVariable,
    UnexpectedType,
    UnknownVariable,
)
from compiler.parser import parse, parse_tree_to_ast

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
        err.report(source)
    except errors.UnexpectedType as err:
        err.report(source)
    except errors.TypeMismatch as err:
        err.report(source)
    except errors.DuplicatedCase as err:
        err.report(source)
    except errors.InexhaustiveMatch as err:
        err.report(source)
    except errors.CompilerError as err:
        print(err)


def _run(
    source: str, type_env: TypeEnvironment, runtime_env: RuntimeEnvironment
) -> Any:
    tree = parse(source)
    ast = parse_tree_to_ast(tree)

    ast.typecheck(type_env)

    return ast.eval(runtime_env)


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
