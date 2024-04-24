from typing import Optional
from compiler.ast.base import Ast
from compiler.compiler import langtypes
from compiler.env import TypeEnvironment
from compiler.lalr import Token


from dataclasses import dataclass


@dataclass
class TypeAnnotation(Ast):
    ty: Token
    generics: Optional["TypeAnnotation"]

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        if self.generics and self.ty == "array":  # TODO: harcoded
            generics = self.generics.typecheck(env)
            self.type = langtypes.Array(generics)
        else:
            self.type = env.get_type(self.ty)

        if self.type is None:
            raise  # TODO
            # raise errors.UnassignableType()
        return self.type
