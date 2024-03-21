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
        err.report(source)
    except errors.UnknownVariable as err:
        err.report(source)
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
