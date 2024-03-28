from dataclasses import dataclass
from typing import Any


@dataclass
class FunctionReturn(Exception):
    """
    Raised by the language runtime to signal the execution of a return
    statement within a function.
    """

    return_value: Any
