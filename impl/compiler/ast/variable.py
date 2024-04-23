from dataclasses import dataclass
from typing_extensions import override

from compiler import errors, langtypes
from compiler.ast.expressions import Expression
from compiler.ast.statements import Statement
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.lalr import Token


@dataclass
class Variable(Expression):
    value: str

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = env.get_var_type(self.value)
        if self.type is None:
            raise errors.UnknownVariable(
                message=f"Variable '{self.value}' not declared in this scope",
                span=self.span,
                variable=self.value,
            )
        else:
            return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        return env.get(self.value)


@dataclass
class VariableDeclaration(Statement):
    ident: str
    rvalue: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        ty = self.rvalue.typecheck(env)
        env.define_var_type(self.ident, ty)

    @override
    def eval(self, env: RuntimeEnvironment):
        rhs = self.rvalue.eval(env)
        env.define(self.ident, rhs)


@dataclass
class Assignment(Statement):
    lvalue: Token
    rvalue: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        lvalue_type = env.get_var_type(self.lvalue)
        if lvalue_type is None:
            raise errors.UndeclaredVariable(
                message=f"Variable '{self.lvalue}' not declared in this scope",
                span=errors.Span.from_token(self.lvalue),
                variable=self.lvalue,
                # TODO: Add help message to use let
            )

        rvalue_type = self.rvalue.typecheck(env)
        if lvalue_type != rvalue_type:
            raise errors.InternalCompilerError("Type mismatch: TODO")  # TODO

    @override
    def eval(self, env: RuntimeEnvironment):
        rhs = self.rvalue.eval(env)
        env.set(self.lvalue, rhs)
