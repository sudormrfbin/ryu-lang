from dataclasses import dataclass

from lark import ast_utils


@dataclass
# TODO: explain requirement of underscore by lark
class _Ast(ast_utils.Ast):
    _type = None

    def generate_code(self):
        pass


@dataclass
class BoolLiteral(_Ast):
    value: bool

    def generate_code(self):
        return "True" if self.value else "False"
