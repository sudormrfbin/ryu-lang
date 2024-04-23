from typing import Any, Optional
from dataclasses import dataclass
from typing_extensions import override

from compiler.ast.base import Ast
from compiler.ast.expressions import Expression
from compiler.ast.struct import StructInitMembers
from compiler.ast.variable import Variable
from compiler.lalr import Token

from compiler.env import FunctionDefScope, RuntimeEnvironment, TypeEnvironment

from compiler import langtypes, langvalues, runtime
from compiler import errors

from compiler.ast.literals import StringLiteral as StringLiteral
from compiler.ast.statements import (
    StatementBlock,
    Statement,
    StatementList as StatementList,
)
from compiler.ast import if_stmt as if_stmt
from compiler.ast import match as match
from compiler.ast import struct as struct
from compiler.ast import variable as variable
from compiler.ast import array as array
from compiler.ast import enum as enum
from compiler.ast import literals as literals
from compiler.ast.annotation import TypeAnnotation


# TODO: Narrow down this type
EvalResult = Any


@dataclass
class PrintStmt(Statement):
    expr: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        self.expr.typecheck(env)

    @override
    def eval(self, env: RuntimeEnvironment):
        print(self.expr.eval(env))


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


@dataclass
class FunctionParam(Ast):
    name: Token
    arg_type: TypeAnnotation

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = self.arg_type.typecheck(env)
        return self.type


@dataclass
class FunctionParams(Ast):
    args: list[FunctionParam]

    def typecheck(self, env: TypeEnvironment) -> langtypes.Function.Params:
        types = [arg.typecheck(env) for arg in self.args]
        self.type = langtypes.Function.Params(types)
        return self.type

    def param_names(self) -> list[str]:
        return [param.name for param in self.args]


@dataclass
class FunctionDefinition(Statement):
    name: Token
    args: Optional[FunctionParams]
    return_type: TypeAnnotation
    body: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment):
        ret_type = self.return_type.typecheck(env)
        params = (
            self.args.typecheck(env) if self.args else langtypes.Function.Params([])
        )

        type = langtypes.Function(
            function_name=self.name,
            arguments=params,
            return_type=ret_type,
        )

        body_env = TypeEnvironment(enclosing=env, fn_scope=FunctionDefScope(ret_type))
        body_env.define_var_type(self.name, type)

        if self.args:
            for arg in self.args.args:
                assert arg.type is not None
                body_env.define_var_type(arg.name, arg.type)

        self.body.typecheck(body_env)

        env.define_var_type(self.name, type)

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        param_names = self.args.param_names() if self.args else []
        env.define(self.name, langvalues.RyuFunction(param_names, self.body))


@dataclass
class ReturnStmt(Statement):
    return_value: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        return_type = self.return_value.typecheck(env)
        if return_type != env.fn_return_type():
            raise  # TODO

    @override
    def eval(self, env: RuntimeEnvironment):
        value = self.return_value.eval(env)
        raise runtime.FunctionReturn(value)


@dataclass
class FunctionArgs(Ast):
    args: list[Expression]

    def typecheck(self, env: TypeEnvironment) -> langtypes.Function.Params:
        types = [arg.typecheck(env) for arg in self.args]
        self.type = langtypes.Function.Params(types)
        return self.type

    def eval(self, env: RuntimeEnvironment) -> list[EvalResult]:
        return [arg.eval(env) for arg in self.args]


@dataclass
class FunctionCall(Expression):  # TODO: rename to FunctionCallOrStructInit
    callee: Variable
    args: Optional[FunctionArgs | StructInitMembers]

    is_fn: bool | None = None

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.callee.type = ctype = env.get_var_type(self.callee.value) or env.get_type(
            self.callee.value
        )
        args = self.args
        match (ctype, args):
            case (langtypes.Function(), FunctionArgs() | None):
                self.is_fn = True
                return self.typecheck_function_call(ctype, args, env)
            case (langtypes.Struct(), StructInitMembers() | None):
                self.is_fn = False
                return self.typecheck_struct_init(ctype, args, env)
            case _:
                raise  # TODO

    def typecheck_function_call(
        self,
        ty: langtypes.Function,
        args: Optional[FunctionArgs],
        env: TypeEnvironment,
    ):
        if args:
            args_type = args.typecheck(env)
        else:
            args_type = langtypes.Function.Params([])

        arg_len, param_len = len(args_type), len(ty.arguments)
        if arg_len < param_len:
            raise  # TODO insufficient args
        if arg_len > param_len:
            raise  # TODO too many args
        if args_type != ty.arguments:
            raise  # TODO type mismatch

        self.type = ty.return_type
        return self.type

    def typecheck_struct_init(
        self,
        ty: langtypes.Struct,
        members: Optional[StructInitMembers],
        env: TypeEnvironment,
    ):
        if members:
            members_type = members.typecheck(env)
        else:
            members_type = langtypes.Struct.Members({})

        mem_len, param_len = len(members_type), len(ty.members)
        if mem_len < param_len:
            raise  # TODO insufficient members
        if mem_len > param_len:
            raise  # TODO too many members
        if members_type != ty.members:
            raise  # TODO type mismatch

        self.type = ty
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        if self.is_fn is True:
            return self.eval_function_call(self.callee.eval(env), env)
        elif self.is_fn is False:
            return self.eval_struct_init(env)
        else:
            assert False

    def eval_function_call(
        self, fn: langvalues.Function, env: RuntimeEnvironment
    ) -> Any:
        args = self.args.eval(env) if self.args else []
        assert isinstance(args, list)

        return fn.call(args, env)

    def eval_struct_init(self, env: RuntimeEnvironment) -> langvalues.StructValue:
        assert isinstance(self.args, StructInitMembers)
        assert isinstance(self.type, langtypes.Struct)

        return langvalues.StructValue(
            name=self.type.struct_name,
            attrs=self.args.eval(env) if self.args else {},
        )


@dataclass
class Term(Expression):
    left: Expression
    op: Token
    right: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, "+" | "-", langtypes.INT:
                self.type = langtypes.INT
            case langtypes.STRING, "+", langtypes.STRING:
                self.type = langtypes.STRING
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[
                        errors.OperandSpan(left_type, self.left.span),
                        errors.OperandSpan(right_type, self.right.span),
                    ],
                )

        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case "+":
                return left + right
            case "-":
                return left - right
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class Factor(Expression):
    left: Expression
    op: Token
    right: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, "*" | "/" | "%", langtypes.INT:
                self.type = langtypes.INT
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[
                        errors.OperandSpan(left_type, self.left.span),
                        errors.OperandSpan(right_type, self.right.span),
                    ],
                )

        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case "*":
                return left * right
            case "/":
                match self.left.type, self.right.type:
                    case langtypes.INT, langtypes.INT:
                        return left // right
                    case _:
                        raise errors.InternalCompilerError(
                            f"{type(self).__name__} recieved invalid operator {self.op}"
                        )
            case "%":
                match self.left.type, self.right.type:
                    case langtypes.INT, langtypes.INT:
                        return left % right
                    case _:
                        raise errors.InternalCompilerError(
                            f"{type(self).__name__} recieved invalid operator {self.op}"
                        )
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class Comparison(Expression):
    left: Expression
    op: Token
    right: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, ">" | "<" | "<=" | ">=", langtypes.INT:
                self.type = langtypes.BOOL
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[
                        errors.OperandSpan(left_type, self.left.span),
                        errors.OperandSpan(right_type, self.right.span),
                    ],
                )

        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case ">":
                return left > right
            case "<":
                return left < right
            case "<=":
                return left <= right
            case ">=":
                return left >= right
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class Logical(Expression):
    left: Expression
    op: Token
    right: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.BOOL, "&&", langtypes.BOOL:
                self.type = langtypes.BOOL
            case langtypes.BOOL, "||", langtypes.BOOL:
                self.type = langtypes.BOOL
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[
                        errors.OperandSpan(left_type, self.left.span),
                        errors.OperandSpan(right_type, self.right.span),
                    ],
                )

        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case "&&":
                return left and right
            case "||":
                return left or right
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class Equality(Expression):
    left: Expression
    op: Token
    right: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        if left_type == right_type and self.op in ("==", "!="):  # pyright: ignore [reportUnnecessaryContains]
            self.type = langtypes.BOOL
        else:
            op_span = errors.Span.from_token(self.op)
            raise errors.InvalidOperationError(
                message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                span=self.span,
                operator=errors.OperatorSpan(self.op, op_span),
                operands=[
                    errors.OperandSpan(left_type, self.left.span),
                    errors.OperandSpan(right_type, self.right.span),
                ],
            )

        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case "==":
                return left == right
            case "!=":
                return left != right
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class UnaryOp(Expression):
    op: Token
    operand: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        operand_type = self.operand.typecheck(env)

        match self.op, operand_type:
            case "+" | "-", langtypes.INT:
                self.type = operand_type
            case "!", langtypes.BOOL:
                self.type = operand_type
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation '{self.op}' for type '{operand_type.name}'",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[errors.OperandSpan(operand_type, self.operand.span)],
                )

        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        result = self.operand.eval(env)
        match self.op:
            case "+":
                return result
            case "-":
                return -result
            case "!":
                return not result
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class EnumLiteralSimple(Expression):
    enum_type: Token
    variant: Token

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = env.get_type(self.enum_type)
        if self.type is None:
            raise  # TODO
            # raise errors.UndeclaredType()
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment) -> langvalues.EnumValue:
        return langvalues.EnumValue(ty=self.enum_type, variant=self.variant)


@dataclass
class EnumLiteralTuple(Expression):
    enum_type: Token
    variant: Token
    inner: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = env.get_type(self.enum_type)
        if self.type is None:
            raise  # TODO
            # raise errors.UndeclaredType()
        if not isinstance(self.type, langtypes.Enum):
            raise  # TODO

        inner_type = self.inner.typecheck(env)
        variant_type = self.type.variant_from_str(self.variant)
        if not isinstance(variant_type, langtypes.Enum.Tuple):
            raise  # TODO

        if variant_type.inner != inner_type:
            raise  # TODO

        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        return langvalues.EnumTupleValue(
            ty=self.enum_type,
            variant=self.variant,
            tuple_value=self.inner.eval(env),
        )
