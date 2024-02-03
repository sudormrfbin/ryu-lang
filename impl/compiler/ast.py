import abc
from typing import Any, Union
import typing
import dataclasses
from dataclasses import dataclass
from typing_extensions import override

from lark import Token, ast_utils
from lark.tree import Meta as LarkMeta

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
    def typecheck(self) -> langtypes.Type:
        pass

    @abc.abstractmethod
    def eval(self) -> EvalResult:
        pass

    def to_dict(self) -> AstDict:
        attrs: dict[str, Any] = {}

        for field in dataclasses.fields(self):
            if SKIP_SERIALIZE in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, _Ast):
                attrs[field.name] = value.to_dict()
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

        return result


class _Expression(_Ast):
    pass


@dataclass
class Term(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self) -> langtypes.Type:
        left_type = self.left.typecheck()
        right_type = self.right.typecheck()

        match left_type, self.op, right_type:
            case langtypes.INT, "+" | "-" | "*", langtypes.INT:
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
    def eval(self):
        left = self.left.eval()
        right = self.right.eval()
        match self.op:
            case "+":
                return left + right
            case "-":
                return left - right
            case "*":
                return left * right
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class UnaryOp(_Expression):
    op: Token
    operand: _Expression

    @override
    def typecheck(self) -> langtypes.Type:
        operand_type = self.operand.typecheck()

        match self.op, operand_type:
            case "+" | "-", langtypes.INT:
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
    def eval(self):
        result = self.operand.eval()
        match self.op:
            case "+":
                return result
            case "-":
                return -result
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class BoolLiteral(_Expression):
    value: bool

    @override
    def typecheck(self) -> langtypes.Type:
        self.type_ = langtypes.BOOL
        return self.type_

    @override
    def eval(self):
        return self.value


@dataclass
class IntLiteral(_Expression):
    value: int

    @override
    def typecheck(self) -> langtypes.Type:
        self.type_ = langtypes.INT
        return self.type_

    @override
    def eval(self):
        return self.value


@dataclass
class StringLiteral(_Expression):
    value: str

    @override
    def typecheck(self) -> langtypes.Type:
        self.type_ = langtypes.STRING
        return self.type_

    @override
    def eval(self):
        return self.value
