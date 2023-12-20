from dataclasses import dataclass

from lark import ast_utils

from . import langtypes


# TODO: explain requirement of underscore by lark
class _Ast(ast_utils.Ast):
    def __init__(self):
        self._type: langtypes.Type | None = None


class _Expression(_Ast):
    pass


@dataclass
class BoolLiteral(_Expression):
    value: bool


@dataclass
class IntLiteral(_Expression):
    value: bool
