from typing import Callable
from textwrap import dedent


def multiline_sanitize(source: str) -> str:
    return dedent(source).strip()


def docstring_source(func: Callable[[str], None]) -> Callable[[], None]:
    source = multiline_sanitize(func.__doc__ or "")

    def wrapper():
        func(source)

    return wrapper
