import abc
from compiler.env import RuntimeEnvironment, TypeEnvironment


from dataclasses import dataclass
from typing_extensions import override

from compiler.ast.base import Ast


class Statement(Ast):
    @abc.abstractmethod
    def typecheck(self, env: TypeEnvironment):
        pass

    @abc.abstractmethod
    def eval(self, env: RuntimeEnvironment):
        pass


@dataclass
class StatementList(Ast):
    stmts: list[Statement]

    def typecheck(self, env: TypeEnvironment):
        for stmt in self.stmts:
            stmt.typecheck(env)

    def eval(self, env: RuntimeEnvironment):
        for child in self.stmts:
            child.eval(env)


@dataclass
class StatementBlock(StatementList):
    @override
    def typecheck(self, env: TypeEnvironment):
        child_env = TypeEnvironment(enclosing=env)
        super().typecheck(child_env)

    @override
    def eval(self, env: RuntimeEnvironment):
        child_env = RuntimeEnvironment(enclosing=env)
        return super().eval(child_env)
