from typing import Literal, Union
import dataclasses
from dataclasses import dataclass

from lark import ast_utils
from lark.tree import Meta as LarkMeta

from . import langtypes
from . import errors

_LispAst = list[Union[str, "_LispAst"]]

SEXP_SKIP_KEY = "sexp_skip"


# TODO: explain requirement of underscore by lark
@dataclass
class _Ast(ast_utils.Ast, ast_utils.WithMeta):
    # InitVar makes meta available on the __post_init__ method
    # and excludes it in the generated __init__.
    meta: dataclasses.InitVar[LarkMeta]
    """Line and column numbers from lark framework.
    Converted to Span for strorage within the class."""

    span: errors.Span = dataclasses.field(init=False, metadata={SEXP_SKIP_KEY: True})
    """Line and column number information."""

    # kw_only is required to make dataclasses play nice with inheritance and
    # fields with default values. https://stackoverflow.com/a/69822584/7115678
    type_: langtypes.Type | None = dataclasses.field(
        default=None, kw_only=True, metadata={SEXP_SKIP_KEY: True}
    )

    def __post_init__(self, meta: LarkMeta):
        self.span = errors.Span.from_meta(meta)

    def typecheck(self):
        pass

    def eval(self):
        pass

    def to_untyped_sexp(self) -> _LispAst:
        classname = type(self).__name__

        lisp_ast: _LispAst = [classname]

        for field in dataclasses.fields(self):
            if SEXP_SKIP_KEY in field.metadata:
                continue

            lisp_ast.append(":")
            lisp_ast.append(field.name)

            value = getattr(self, field.name)
            if isinstance(value, _Ast):
                lisp_ast.append(value.to_untyped_sexp())
            else:
                lisp_ast.append(str(value))

        return lisp_ast

    def to_typed_sexp(self) -> _LispAst:
        classname = type(self).__name__
        assert self.type_ is not None
        type_ = self.type_.name

        lisp_ast: _LispAst = [classname, type_]

        for field in dataclasses.fields(self):
            if SEXP_SKIP_KEY in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, _Ast):
                lisp_ast.append(":")
                lisp_ast.append(field.name)
                lisp_ast.append(value.to_typed_sexp())

        return lisp_ast


class _Expression(_Ast):
    pass


@dataclass
class Term(_Expression):
    left: _Expression
    op: Literal["+", "-"]
    right: _Expression

    def typecheck(self):
        self.left.typecheck()
        left_type = self.left.type_
        self.right.typecheck()
        right_type = self.right.type_

        match left_type, self.op, right_type:
            case langtypes.INT, "+" | "-", langtypes.INT:
                self.type_ = langtypes.INT
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                    span=self.span,
                    operator=(self.op, op_span),
                    operands=[
                        (left_type, self.left.span),
                        (right_type, self.right.span),
                    ],
                )

        self.type_ = self.left.type_

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
    op: Literal["+", "-"]
    operand: _Expression

    def typecheck(self):
        self.operand.typecheck()
        operand_type = self.operand.type_

        # NOTE: self.op is a lark.lexer.Token, not actually a string
        match self.op, operand_type:
            case "+" | "-", langtypes.INT:
                self.type_ = operand_type
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation '{self.op}' for type '{operand_type.name}'",
                    span=self.span,
                    operator=(self.op, op_span),
                    operands=[(operand_type, self.operand.span)],
                )

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

    def typecheck(self):
        self.type_ = langtypes.BOOL

    def eval(self):
        return self.value


@dataclass
class IntLiteral(_Expression):
    value: int

    def typecheck(self):
        self.type_ = langtypes.INT

    def eval(self):
        return self.value
