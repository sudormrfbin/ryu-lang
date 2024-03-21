from dataclasses import dataclass
from typing_extensions import override


@dataclass
class EnumValue:
    ty: str
    variant: str

    @override
    def __str__(self) -> str:
        return f"{self.ty}::{self.variant}"

    @override
    def __hash__(self) -> int:
        return hash(repr(self))
