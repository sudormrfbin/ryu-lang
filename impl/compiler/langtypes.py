from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Sequence, TypeAlias
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

    @classmethod
    def from_str_with_generics(
        cls,
        ident: str,
        generics: Type,
        env: TypeEnvironment,
    ) -> Optional["Type"]:
        if ident == "array":
            return Array(generics)

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
    members: Members

    @dataclass
    class Members(PrimitiveType):
        types: dict[str, Type]

        def __len__(self) -> int:
            return len(self.types)


@dataclass
class Enum(UserDefinedType):
    enum_name: str
    members: list[EnumVariantSimple | EnumVariantTuple]
    span: Span

    @property
    @override
    def name(self) -> str:
        return self.enum_name

    def variant_from_str(
        self, name: str
    ) -> EnumVariantSimple | EnumVariantTuple | None:
        for mem in self.members:
            if mem.name == name:
                return mem
        return None


@dataclass
class EnumVariantSimple:
    name: str


@dataclass
class EnumVariantTuple:
    name: str
    inner: Type


EnumVariants: TypeAlias = EnumVariantSimple | EnumVariantTuple


@dataclass
class Array(PrimitiveType):
    ty: Type

    @property
    @override
    def name(self) -> str:
        return f"Array<{self.ty.name}>"


@dataclass
class UntypedArray(PrimitiveType):
    pass


@dataclass
class Function(PrimitiveType):
    function_name: str
    arguments: Params
    return_type: Type


@dataclass
class Params(PrimitiveType):
    types: list[Type]

    def __len__(self) -> int:
        return len(self.types)


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
