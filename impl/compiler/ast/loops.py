from dataclasses import dataclass
from typing_extensions import override

from compiler import errors, langtypes
from compiler.ast.expressions import Expression
from compiler.ast.statements import Statement, StatementBlock
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.lalr import Token


@dataclass
class WhileStmt(Statement):
    cond: Expression
    true_block: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment):
        expr_type = self.cond.typecheck(env)
        if expr_type != langtypes.BOOL:
            raise errors.UnexpectedType(
                message="Unexpected type for while condition",
                span=self.cond.span,
                expected_type=langtypes.BOOL,
                actual_type=expr_type,
            )

        self.true_block.typecheck(env)

    @override
    def eval(self, env: RuntimeEnvironment):
        while self.cond.eval(env) is True:
            self.true_block.eval(env)


@dataclass
class ForStmt(Statement):
    var: Token
    arr_name: Expression
    stmts: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment):
        array_type = self.arr_name.typecheck(env)
        if not isinstance(array_type, langtypes.Array) and not isinstance(
            array_type, langtypes.String
        ):
            raise errors.UnexpectedType(
                message="Unexpected type",
                span=self.arr_name.span,
                expected_type=langtypes.Array(array_type),
                actual_type=array_type,
            )

        child_env = TypeEnvironment(enclosing=env)
        child_env.define_var_type(self.var, array_type)

        self.stmts.typecheck(child_env)

    @override
    def eval(self, env: RuntimeEnvironment):
        arr = self.arr_name.eval(env)
        for element in arr:
            loop_env = RuntimeEnvironment(env)
            loop_env.define(self.var, element)
            self.stmts.eval(loop_env)


@dataclass
class ForStmtInt(Statement):
    var: Token
    start: Expression
    end: Expression
    stmts: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment):
        start_type = self.start.typecheck(env)
        end_type = self.end.typecheck(env)
        if not isinstance(start_type, langtypes.Int) and not isinstance(
            end_type, langtypes.Int
        ):
            raise  # TODO

        child_env = TypeEnvironment(enclosing=env)
        child_env.define_var_type(self.var, start_type)

        self.stmts.typecheck(child_env)

    @override
    def eval(self, env: RuntimeEnvironment):
        start_index = self.start.eval(env)
        end_index = self.end.eval(env)
        for i in range(start_index, end_index):
            loop_env = RuntimeEnvironment(env)
            loop_env.define(self.var, i)
            self.stmts.eval(loop_env)
