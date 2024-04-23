from dataclasses import dataclass

from typing_extensions import override

from compiler import langtypes
from compiler.ast.expressions import Expression
from compiler.env import RuntimeEnvironment, TypeEnvironment


@dataclass
class BoolLiteral(Expression):
    value: bool

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.BOOL
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class IntLiteral(Expression):
    value: int

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.INT
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class StringLiteral(Expression):
    value: str

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.STRING
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value
