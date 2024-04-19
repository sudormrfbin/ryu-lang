from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence, TypeAlias
from typing_extensions import override


if TYPE_CHECKING:
    from compiler.errors import Span


class Type:
    @property
    def name(self) -> str:
        return type(self).__name__


class Placeholder(Type):
    pass


class Bool(Type):
    pass


class Int(Type):
    pass


class String(Type):
    pass


class Block(Type):
    pass


@dataclass
class ReturnBlock(Block):
    return_type: Type
    return_stmt_span: Span


@dataclass
class Struct(Type):
    struct_name: str
    members: Members

    @dataclass
    class Members(Type):
        types: dict[str, Type]

        def __len__(self) -> int:
            return len(self.types)


@dataclass
class Enum(Type):
    enum_name: str  # TODO: rename to name
    members: list[Variants]
    span: Span

    @property
    @override
    def name(self) -> str:
        return self.enum_name

    def variant_from_str(self, name: str) -> Variants | None:
        for mem in self.members:
            if mem.name == name:
                return mem
        return None

    @dataclass
    class Simple:
        name: str

    @dataclass
    class Tuple:
        name: str
        inner: Type

    Variants: TypeAlias = Simple | Tuple


@dataclass
class Array(Type):
    ty: Type

    @property
    @override
    def name(self) -> str:
        return f"Array<{self.ty.name}>"


@dataclass
class UntypedArray(Type):
    pass


@dataclass
class Function(Type):
    function_name: str
    arguments: Params
    return_type: Type

    @dataclass
    class Params(Type):
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


Primitive = Int | Bool | String


def name(ty: Primitive) -> str:
    match ty:
        case Int():
            return "int"
        case Bool():
            return "bool"
        case String():
            return "string"
