import abc
from typing import Any, Union
import typing
import dataclasses
from dataclasses import dataclass
from typing_extensions import override

from lark import Token, ast_utils
from lark.tree import Meta as LarkMeta

from .env import RuntimeEnvironment, TypeEnvironment

from . import langtypes
from . import errors

_LispAst = list[Union[str, "_LispAst"]]

SKIP_SERIALIZE = "skip_serialize"

# TODO: Narrow down this type
EvalResult = Any

AstDict = dict[typing.Type["_Ast"], dict[str, Any]]

# In AstTypeDict, the key type will always correspond to exactly one value type:
# _Ast -> Type
# str -> AstTypeDict
# Since this cannot be expressed in the type system, we settle for a union type
# which introduces two extra invalid states (_Ast -> AstTypeDict & str -> Type)
AstTypeDict = dict[
    typing.Type["_Ast"] | str, typing.Type[langtypes.Type] | "AstTypeDict"
]


# TODO: explain requirement of underscore by lark
@dataclass
class _Ast(abc.ABC, ast_utils.Ast, ast_utils.WithMeta):
    # InitVar makes meta available on the __post_init__ method
    # and excludes it in the generated __init__.
    meta: dataclasses.InitVar[LarkMeta]
    """Line and column numbers from lark framework.
    Converted to Span for strorage within the class."""

    span: errors.Span = dataclasses.field(init=False, metadata={SKIP_SERIALIZE: True})
    """Line and column number information."""

    # kw_only is required to make dataclasses play nice with inheritance and
    # fields with default values. https://stackoverflow.com/a/69822584/7115678
    type_: langtypes.Type | None = dataclasses.field(
        default=None, kw_only=True, metadata={SKIP_SERIALIZE: True}
    )

    def __post_init__(self, meta: LarkMeta):
        self.span = errors.Span.from_meta(meta)

    @abc.abstractmethod
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        pass

    @abc.abstractmethod
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        pass

    def to_dict(self) -> AstDict:
        attrs: dict[str, Any] = {}

        for field in dataclasses.fields(self):
            if SKIP_SERIALIZE in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, _Ast):
                attrs[field.name] = value.to_dict()
            elif isinstance(value, list) and isinstance(value[0], _Ast):
                attrs[field.name] = [v.to_dict() for v in value]  # type: ignore
            else:
                attrs[field.name] = value

        return {type(self): attrs}

    def to_type_dict(
        self,
    ) -> AstTypeDict:
        assert self.type_ is not None

        result: AstTypeDict = {}
        result[type(self)] = type(self.type_)

        for field in dataclasses.fields(self):
            if SKIP_SERIALIZE in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, _Ast):
                result[field.name] = value.to_type_dict()
            elif isinstance(value, list) and isinstance(value[0], _Ast):
                result[field.name] = [v.to_type_dict() for v in value]  # type: ignore

        return result


class _Statement(_Ast):
    pass


@dataclass
class StatementList(_Ast, ast_utils.AsList):
    stmts: list[_Statement]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        for child in self.stmts:
            child.typecheck(env)

        self.type_ = langtypes.BLOCK
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        for child in self.stmts:
            child.eval(env)


class _Expression(_Statement):
    pass


@dataclass
class VariableDeclaration(_Statement):
    ident: str
    rvalue: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = self.rvalue.typecheck(env)
        env.define(self.ident, self.type_)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        rhs = self.rvalue.eval(env)
        env.define(self.ident, rhs)


@dataclass
class Assignment(_Statement):
    lvalue: Token
    rvalue: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        lvalue_type = env.get(self.lvalue)
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

        self.type_ = rvalue_type
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        rhs = self.rvalue.eval(env)
        env.define(self.lvalue, rhs)


@dataclass
class IfStmt(_Statement):
    cond: _Expression
    true_block: StatementList

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        expr_type = self.cond.typecheck(env)
        if expr_type != langtypes.BOOL:
            raise errors.UnexpectedType(
                message="Unexpected type for if condition",
                span=self.cond.span,
                expected_type=langtypes.BOOL,
                actual_type=expr_type,
            )

        self.true_block.typecheck(env)

        self.type_ = langtypes.BLOCK
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        if self.cond.eval(env) is True:
            self.true_block.eval(env)


@dataclass
class Term(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, "+" | "-", langtypes.INT:
                self.type_ = langtypes.INT
            case langtypes.STRING, "+", langtypes.STRING:
                self.type_ = langtypes.STRING
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

        return self.type_

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
class Factor(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, "*" | "/" | "%", langtypes.INT:
                self.type_ = langtypes.INT
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

        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case "*":
                return left * right
            case "/":
                match self.left.type_, self.right.type_:
                    case langtypes.INT, langtypes.INT:
                        return left // right
                    case _:
                        raise errors.InternalCompilerError(
                            f"{type(self).__name__} recieved invalid operator {self.op}"
                        )
            case "%":
                match self.left.type_, self.right.type_:
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
class Comparison(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, ">" | "<" | "<=" | ">=", langtypes.INT:
                self.type_ = langtypes.INT
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

        return self.type_

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
class Logical(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.BOOL, "&&", langtypes.BOOL:
                self.type_ = langtypes.BOOL
            case langtypes.BOOL, "||", langtypes.BOOL:
                self.type_ = langtypes.BOOL
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

        return self.type_

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
class Equality(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, "==", langtypes.INT:
                self.type_ = langtypes.BOOL
            case langtypes.INT, "!=", langtypes.INT:
                self.type_ = langtypes.BOOL
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

        return self.type_

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
class UnaryOp(_Expression):
    op: Token
    operand: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        operand_type = self.operand.typecheck(env)

        match self.op, operand_type:
            case "+" | "-", langtypes.INT:
                self.type_ = operand_type
            case "!", langtypes.BOOL:
                self.type_ = operand_type
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation '{self.op}' for type '{operand_type.name}'",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[errors.OperandSpan(operand_type, self.operand.span)],
                )

        return self.type_

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
class BoolLiteral(_Expression):
    value: bool

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = langtypes.BOOL
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class IntLiteral(_Expression):
    value: int

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = langtypes.INT
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class StringLiteral(_Expression):
    value: str

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = langtypes.STRING
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class Variable(_Expression):
    value: str

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = env.get(self.value)
        if self.type_ is None:
            raise errors.UnknownVariable(
                message=f"Variable '{self.value}' not declared in this scope",
                span=self.span,
                variable=self.value,
            )
        else:
            return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        return env.get(self.value)
