from dataclasses import dataclass
from typing_extensions import override

from compiler.ast.expressions import Expression
from compiler.ast.statements import Statement
from compiler.env import RuntimeEnvironment, TypeEnvironment


@dataclass
class PrintStmt(Statement):
    expr: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        self.expr.typecheck(env)

    @override
    def eval(self, env: RuntimeEnvironment):
        print(self.expr.eval(env))
