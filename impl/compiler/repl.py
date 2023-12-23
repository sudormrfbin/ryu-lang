from typing import TYPE_CHECKING

from .compiler import run
from . import errors

from error_report.error_report import report_error

if TYPE_CHECKING:
    from error_report.error_report import Message


def repl() -> None:
    while True:
        try:
            source = input("> ").strip()
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
            labels = []
            for type_, span in err.operands:
                msg: Message = ["This is of type ", (type_.name, type_.name)]
                labels.append(
                    (
                        msg,
                        (span.start_pos, span.end_pos),
                    )
                )

            operand_type = err.operands[0][0]
            message: Message = [
                f"Invalid operation {err.operator[0]} for type ",
                (operand_type.name, operand_type.name),
            ]

            report_error(
                source=source,
                start_pos=err.span.start_pos,
                message=message,
                code=err.code,
                labels=labels,
            )
        except errors.CompilerError as err:
            print(err)
