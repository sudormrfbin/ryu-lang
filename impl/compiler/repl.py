from typing import TYPE_CHECKING

from .compiler import run
from . import errors
from .errors import OperandSpan

# error_report submodule is generated dynamically by pyo3 on the rust
# side. Hence pyright cannot detect the source file.
from error_report.error_report import report_error  # pyright: ignore [reportMissingModuleSource]

if TYPE_CHECKING:
    from error_report.error_report import Message, Mark  # pyright: ignore [reportMissingModuleSource]


def repl() -> None:
    while True:
        try:
            source = input(">> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            break

        if not source:
            continue

        try:
            result = run(source)
            if result is not None:
                print(result)
        except errors.InvalidOperationError as err:
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
        except errors.CompilerError as err:
            print(err)
