from typing import Any, Callable
from textwrap import dedent


def multiline_sanitize(source: str) -> str:
    return dedent(source).strip()


def docstring_source(func: Callable[[str], None]) -> Callable[[], None]:
    source = multiline_sanitize(func.__doc__ or "")

    def wrapper():
        func(source)

    return wrapper


def docstring_source_with_snapshot(
    func: Callable[[str, Any], None],
) -> Callable[[Any], None]:
    source = multiline_sanitize(func.__doc__ or "")

    def wrapper(snapshot: Any):
        func(source, snapshot)

    return wrapper
