import abc
import dataclasses
from dataclasses import dataclass
from typing import Any

from compiler import langtypes
from compiler.ast.base import Ast
from compiler.env import RuntimeEnvironment, TypeEnvironment


@dataclass
class Expression(Ast):
    # kw_only is required to make dataclasses play nice with inheritance and
    # fields with default values. https://stackoverflow.com/a/69822584/7115678
    type: langtypes.Type | None = dataclasses.field(
        default=None,
        kw_only=True,
    )

    @abc.abstractmethod
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        pass

    @abc.abstractmethod
    def eval(self, env: RuntimeEnvironment) -> Any:
        pass
