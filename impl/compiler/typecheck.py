from .ast import _Ast, BoolLiteral
from . import langtypes as types


def type_check(ast: _Ast) -> _Ast:
    match ast:
        case BoolLiteral():
            ast._type = types.BOOL

    return ast
