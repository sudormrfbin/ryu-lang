from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from typing_extensions import override
from compiler import runtime

from compiler.env import RuntimeEnvironment

if TYPE_CHECKING:
    from compiler.ast import StatementBlock


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


class Function:
    @abstractmethod
    def call(self, args: list[Any], env: "RuntimeEnvironment") -> Any:
        pass


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
