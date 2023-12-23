from .compiler import run
from . import errors

from error_report.error_report import report_error


def repl():
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
                labels.append(
                    (
                        f"This is of type {type_.name}",
                        (span.start_pos, span.end_pos),
                    )
                )

            report_error(
                source=source,
                start_pos=err.span.start_pos,
                message=err.message,
                code=err.code,
                labels=labels,
            )
        except errors.CompilerError as err:
            print(err)
