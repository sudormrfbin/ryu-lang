from lark import Lark, ast_utils, Transformer

import sys
from dataclasses import dataclass
from pprint import pprint

this_module = sys.modules[__name__]


class _Ast(ast_utils.Ast):
    pass


@dataclass
class BoolLiteral(_Ast):
    value: bool

    def __str__(self):
        return "True" if self.value else "False"


class LarkTreeToAstTransformer(Transformer):
    def TRUE(self, _):
        return True

    def FALSE(self, _):
        return False


transformer = ast_utils.create_transformer(this_module, LarkTreeToAstTransformer())


def transpile(ast: _Ast) -> str:
    return str(ast)


with open("g.lark", "r") as f:
    parser = Lark(f.read(), parser="lalr")

# while True:
# inp = input("> ")
with open("input.lang", "r") as f:
    inp = f.read()
tree = parser.parse(inp)
pprint(tree)
print()

print(tree.pretty())

ast = transformer.transform(tree)
pprint(ast)

print(transpile(ast))
