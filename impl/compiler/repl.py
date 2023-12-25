from typing import TYPE_CHECKING

from .compiler import run
from . import errors

from error_report.error_report import report_error

if TYPE_CHECKING:
    from error_report.error_report import Message, Mark


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
            for type_, span in err.operands:
                msg: Message = ["This is of type ", (type_.name, type_.name)]
                labels.append(
                    (
                        msg,
                        type_.name,
                        (span.start_pos, span.end_pos),
                    )
                )

            operator = err.operator[0]
            message: Message
            match err.operands:
                case [(op_type, _)]:
                    message = [
                        f"Invalid operation '{operator}' for type ",
                        (op_type.name, op_type.name),
                    ]
                case [(op_type1, _), (op_type2, _)]:
                    message = [
                        f"Invalid operation '{operator}' for types ",
                        (op_type1.name, op_type1.name),
                        " and ",
                        (op_type2.name, op_type2.name),
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
