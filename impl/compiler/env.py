from typing import Any

from .errors import InternalCompilerError


class RuntimeEnvironment:
    values: dict[str, Any]

    def __init__(self):
        self.values = {}

    def define(self, name: str, value: Any):
        # shadowing is allowed
        self.values[name] = value

    def get(self, name: str) -> Any:
        try:
            return self.values[name]
        except KeyError:
            raise InternalCompilerError(f"Variable {name} not defined at runtime")
