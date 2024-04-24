from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar
from typing_extensions import override
from compiler import langtypes, runtime

from compiler.env import RuntimeEnvironment

if TYPE_CHECKING:
    from impl.compiler.ast.statements import StatementBlock


@dataclass
class EnumValue:
    ty: str
    variant: str

    @override
    def __str__(self) -> str:
        return f"{self.ty}::{self.variant}"

    @override
    def __hash__(self) -> int:
        return hash(repr(self))


@dataclass
class EnumTupleValue(EnumValue):
    tuple_value: Any

    @override
    def __str__(self) -> str:
        return f"{self.ty}::{self.variant}({self.tuple_value})"

    @override
    def __hash__(self) -> int:
        return hash(repr(self))


@dataclass
class StructValue:
    name: str
    attrs: dict[str, Any]

    @override
    def __str__(self) -> str:
        attrs = ", ".join(f"{attr}={value}" for attr, value in self.attrs)
        return f"{self.name}({attrs})"

    @override
    def __hash__(self) -> int:
        return hash(repr(self))

    def set_attr(self, member: str, value: Any):
        self.attrs[member] = value

    def get_attr(self, member: str) -> Any:
        return self.attrs[member]

class Function:
    @abstractmethod
    def call(self, args: list[Any], env: "RuntimeEnvironment") -> Any:
        pass


class BuiltinFunction(Function):
    TYPE: ClassVar[langtypes.Function]


@dataclass
class RyuFunction(Function):
    param_names: list[str]
    body: "StatementBlock"

    @override
    def call(self, args: list[Any], env: "RuntimeEnvironment") -> Any:
        child_env = RuntimeEnvironment(enclosing=env)

        for name, arg in zip(self.param_names, args):
            child_env.define(name, arg)

        try:
            self.body.eval(child_env)
        except runtime.FunctionReturn as ret:
            return ret.return_value
