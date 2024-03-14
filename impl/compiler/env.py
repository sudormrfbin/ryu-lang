from typing import Any, Optional

from .errors import InternalCompilerError
from . import langtypes


class TypeEnvironment:
    values: dict[str, langtypes.Type]

    def __init__(self):
        self.values = {}

    def define(self, name: str, value: langtypes.Type):
        self.values[name] = value

    def get(self, name: str) -> Optional[langtypes.Type]:
        return self.values.get(name)


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
