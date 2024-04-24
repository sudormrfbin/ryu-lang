from dataclasses import dataclass
from typing_extensions import override

from compiler.ast.expressions import Expression

from compiler.env import RuntimeEnvironment, TypeEnvironment

from compiler.ast.literals import StringLiteral as StringLiteral
from compiler.ast.statements import Statement

from compiler.ast import if_stmt as if_stmt
from compiler.ast import match as match
from compiler.ast import struct as struct
from compiler.ast import variable as variable
from compiler.ast import array as array
from compiler.ast import enum as enum
from compiler.ast import function as function
from compiler.ast import literals as literals
from compiler.ast import operators as operators
from compiler.ast import loops as loops
from compiler.ast import statements as statements

from compiler.ast.annotation import TypeAnnotation as TypeAnnotation


@dataclass
class PrintStmt(Statement):
    expr: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        self.expr.typecheck(env)

    @override
    def eval(self, env: RuntimeEnvironment):
        print(self.expr.eval(env))
