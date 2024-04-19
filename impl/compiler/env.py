from dataclasses import dataclass
from typing import Any, Optional
from typing_extensions import Self

from compiler.errors import InternalCompilerError
from compiler import langtypes


@dataclass
class FunctionDefScope:
    return_type: langtypes.Type


class TypeEnvironment:
    parent: Optional[Self]
    values: dict[str, langtypes.Type]
    """
    Map from variable name to it's type.
    """

    types: dict[str, langtypes.Type]
    """
    Map from type name to type.
    """

    fn_scope: Optional[FunctionDefScope]

    def __init__(
        self,
        enclosing: Optional[Self] = None,
        fn_scope: Optional[FunctionDefScope] = None,
    ):
        self.values = {}
        self.types = {}
        self.parent = enclosing
        self.fn_scope = fn_scope

    def define_var_type(self, name: str, value: langtypes.Type):
        self.values[name] = value

    def get_var_type(self, name: str) -> Optional[langtypes.Type]:
        current = self

        while current is not None:
            if (type_ := current.values.get(name)) is not None:
                return type_
            current = current.parent

        return None

    def define_type(self, type_name: str, type: langtypes.Type):
        self.types[type_name] = type

    def get_type(self, type: str) -> Optional[langtypes.Type]:
        current = self

        while current is not None:
            if (type_ := current.types.get(type)) is not None:
                return type_
            current = current.parent

        return None

    def fn_return_type(self) -> Optional[langtypes.Type]:
        current = self

        while current is not None:
            if (ret := current.fn_scope) is not None:
                return ret.return_type
            current = current.parent

        return None


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
