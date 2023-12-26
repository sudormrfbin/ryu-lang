import abc
from typing import Any, Union
import dataclasses
from dataclasses import dataclass

from lark import Token, ast_utils
from lark.tree import Meta as LarkMeta

from . import langtypes
from . import errors

_LispAst = list[Union[str, "_LispAst"]]

SKIP_SERIALIZE = "skip_serialize"

# TODO: Narrow down this type
EvalResult = Any


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

    def to_dict(self) -> dict:
        attrs = {}

        for field in dataclasses.fields(self):
            if SKIP_SERIALIZE in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, _Ast):
                attrs[field.name] = value.to_dict()
            else:
                attrs[field.name] = value

        return {type(self): attrs}

    def to_type_dict(self) -> dict:
        assert self.type_ is not None

        result: dict = {}
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

    def typecheck(self) -> langtypes.Type:
        left_type = self.left.typecheck()
        right_type = self.right.typecheck()

        match left_type, self.op, right_type:
            case langtypes.INT, "+" | "-", langtypes.INT:
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

    def eval(self):
        left = self.left.eval()
        right = self.right.eval()
        match self.op:
            case "+":
                return left + right
            case "-":
                return left - right


@dataclass
class UnaryOp(_Expression):
    op: Token
    operand: _Expression

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

    def eval(self):
        result = self.operand.eval()
        match self.op:
            case "+":
                return result
            case "-":
                return -result


@dataclass
class BoolLiteral(_Expression):
    value: bool

    def typecheck(self) -> langtypes.Type:
        self.type_ = langtypes.BOOL
        return self.type_

    def eval(self):
        return self.value


@dataclass
class IntLiteral(_Expression):
    value: int

    def typecheck(self) -> langtypes.Type:
        self.type_ = langtypes.INT
        return self.type_

    def eval(self):
        return self.value
