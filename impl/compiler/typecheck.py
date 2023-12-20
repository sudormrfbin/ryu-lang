from . import ast
from . import langtypes as types


def type_check(node: ast._Ast) -> ast._Ast:
    match node:
        case ast.BoolLiteral():
            node._type = types.BOOL
        case ast.IntLiteral():
            node._type = types.INT

    return node
