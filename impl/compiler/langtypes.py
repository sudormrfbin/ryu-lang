from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from compiler.env import TypeEnvironment


class Type:
    @property
    def name(self) -> str:
        return type(self).__name__

    @classmethod
    def from_str(cls, ident: str, env: TypeEnvironment) -> Optional["Type"]:
        if ident in PRIMITIVE_TYPES:
            return PRIMITIVE_TYPES[ident]

        ty = env.get(ident)
        if isinstance(ty, UserDefinedType):
            return ty

        return None


class PrimitiveType(Type):
    pass


class UserDefinedType(Type):
    pass


class Bool(PrimitiveType):
    pass


class Int(PrimitiveType):
    pass


class String(PrimitiveType):
    pass


class Block(Type):
    pass


@dataclass
class Struct(UserDefinedType):
    struct_name: str
    members: dict[str, Type]


@dataclass
class Enum(UserDefinedType):
    enum_name: str
    members: list[str]

@dataclass
class Array(PrimitiveType):
    ty: Type

@dataclass
class Function(UserDefinedType):
    function_name:str
    arguments: list[tuple[str, Type]]
    return_type: Type

BOOL = Bool()
INT = Int()
STRING = String()
BLOCK = Block()


PRIMITIVE_TYPES: dict[str, Type] = {
    "bool": BOOL,
    "int": INT,
    "string": STRING,
}
