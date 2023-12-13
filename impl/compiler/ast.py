from dataclasses import dataclass

from lark import ast_utils


class _Ast(ast_utils.Ast):
    def generate_code(self):
        pass


@dataclass
class BoolLiteral(_Ast):
    value: bool

    def generate_code(self):
        return "True" if self.value else "False"
