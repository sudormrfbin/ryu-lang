from typing import Any, Optional
from typing_extensions import Self

from compiler.errors import InternalCompilerError
from compiler import langtypes


class TypeEnvironment:
    parent: Optional[Self]
    values: dict[str, langtypes.Type]

    def __init__(self, enclosing: Optional[Self] = None):
        self.values = {}
        self.parent = enclosing

    def define(self, name: str, value: langtypes.Type):
        self.values[name] = value

    def get(self, name: str) -> Optional[langtypes.Type]:
        current = self

        while current is not None:
            if (type_ := current.values.get(name)) is not None:
                return type_
            current = current.parent

        return None

    def is_global(self) -> bool:
        return self.parent is None


class RuntimeEnvironment:
    parent: Optional[Self]
    values: dict[str, Any]

    def __init__(self, enclosing: Optional[Self] = None):
        self.values = {}
        self.parent = enclosing

    def define(self, name: str, value: Any):
        """
        Define a new variable in the current scope.
        """
        # shadowing is allowed
        self.values[name] = value

    def set(self, name: str, value: Any):
        """
        Find the scope in which the variable is defined and set it to a new
        value in that scope. Searches up the lexical scope heirarchy.
        """
        current = self

        while current is not None:
            if current.values.get(name) is not None:
                current.values[name] = value
                return
            current = current.parent

        raise InternalCompilerError(f"Variable {name} could not be found in any scope")

    def get(self, name: str) -> Any:
        current = self

        while current is not None:
            if (value := current.values.get(name)) is not None:
                return value
            current = current.parent

        raise InternalCompilerError(f"Variable {name} not defined at runtime")

    def is_global(self) -> bool:
        return self.parent is None
