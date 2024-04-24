from typing import Optional
from compiler import errors, langtypes
from compiler.ast.expressions import Expression
from compiler.ast.statements import Statement, StatementBlock
from compiler.env import RuntimeEnvironment, TypeEnvironment


from dataclasses import dataclass
from typing_extensions import override

from compiler.ast.base import Ast


@dataclass
class IfStmt(Ast):
    cond: Expression
    true_block: StatementBlock

    def typecheck(self, env: TypeEnvironment):
        expr_type = self.cond.typecheck(env)
        if expr_type != langtypes.BOOL:
            raise errors.UnexpectedType(
                message="Unexpected type for if condition",
                span=self.cond.span,
                expected_type=langtypes.BOOL,
                actual_type=expr_type,
            )

        self.true_block.typecheck(env)

    def eval(self, env: RuntimeEnvironment) -> bool:
        if self.cond.eval(env) is True:
            self.true_block.eval(env)
            return True

        return False


@dataclass
class IfChain(Statement):
    if_stmt: IfStmt
    else_if_ladder: Optional["ElseIfLadder"]
    else_block: Optional[StatementBlock]

    @override
    def typecheck(self, env: TypeEnvironment):
        self.if_stmt.typecheck(env)
        if self.else_block:
            self.else_block.typecheck(env)
        if self.else_if_ladder:
            self.else_if_ladder.typecheck(env)

    @override
    def eval(self, env: RuntimeEnvironment):
        if self.if_stmt.eval(env):
            # if condition evaluates to true, stop the if-chain
            return

        if self.else_if_ladder:
            if self.else_if_ladder.eval(env) is True:
                # one of the else-if blocks executed, stop the if-chain
                return

        if self.else_block:
            self.else_block.eval(env)


@dataclass
class ElseIfStmt(IfStmt):
    pass


@dataclass
class ElseIfLadder(Ast):
    blocks: list[ElseIfStmt]

    def typecheck(self, env: TypeEnvironment):
        for block in self.blocks:
            block.typecheck(env)

    def eval(self, env: RuntimeEnvironment) -> bool:
        """
        Returns True if any of the else if blocks execute.
        """
        for block in self.blocks:
            if block.eval(env) is True:
                return True
        return False
