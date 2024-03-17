from typing import Callable
from textwrap import dedent


def docstring_source(func: Callable[[str], None]) -> Callable[[], None]:
    source = dedent(func.__doc__ or "").strip()

    def wrapper():
        func(source)

    return wrapper
