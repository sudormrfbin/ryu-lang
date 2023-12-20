from dataclasses import dataclass

from lark import ast_utils

from . import langtypes


# TODO: explain requirement of underscore by lark
class _Ast(ast_utils.Ast):
    def __init__(self):
        self._type: langtypes.Type | None = None


@dataclass
class BoolLiteral(_Ast):
    value: bool


@dataclass
class IntLiteral(_Ast):
    value: bool
