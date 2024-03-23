from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, Sequence
from typing_extensions import override


if TYPE_CHECKING:
    from compiler.env import TypeEnvironment
    from compiler.errors import Span


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


class Placeholder(Type):
    pass


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
class ReturnBlock(Block):
    return_type: Type
    return_stmt_span: Span


@dataclass
class Struct(UserDefinedType):
    struct_name: str
    members: dict[str, Type]


@dataclass
class Enum(UserDefinedType):
    enum_name: str
    members: list[str]

    @property
    @override
    def name(self) -> str:
        return self.enum_name


@dataclass
class Array(PrimitiveType):
    ty: Type


@dataclass
class Function(PrimitiveType):
    function_name: str
    arguments: Params
    return_type: Type


@dataclass
class Params(PrimitiveType):
    types: list[Type]


BOOL = Bool()
INT = Int()
STRING = String()
BLOCK = Block()
PLACEHOLDER = Placeholder()


PRIMITIVE_TYPES: dict[str, Type] = {
    "bool": BOOL,
    "int": INT,
    "string": STRING,
}


def resolve_blocks_type(types: Sequence[Type]) -> Block:
    resolved = BLOCK
    for ty in types:
        match (resolved, ty):
            case (Block(), ReturnBlock()):
                resolved = ty
            case (ReturnBlock(), ReturnBlock()):
                if resolved.return_type != ty.return_type:
                    raise  # TODO different return types
            case _:
                pass

    return resolved
