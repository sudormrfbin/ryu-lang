from types import UnionType
from typing import TYPE_CHECKING, Any, Container, Sequence, Type, TypeGuard, TypeVar

from compiler import langtypes, langvalues
from compiler.langvalues import EnumValue


if TYPE_CHECKING:
    from compiler.ast import EnumPattern
    from compiler.ast import ArrayPattern
    from compiler.ast import BoolLiteral, WildcardPattern
    from compiler.errors import Span


class MatcherCaseDuplicated(Exception):
    def __init__(self, previous_case_span: "Span"):
        self.previous_case_span = previous_case_span
        super().__init__()


class Wildcard:
    pass


WILDCARD = Wildcard()


class BoolPatternMatcher:
    def __init__(self) -> None:
        self.cases: dict[bool | Wildcard, Span] = {}

    def add_case(self, arm: "BoolLiteral | WildcardPattern"):
        from compiler.ast import BoolLiteral, WildcardPattern

        match arm:
            case BoolLiteral():
                val = arm.value
            case WildcardPattern():
                val = WILDCARD

        if val in self.cases:
            raise MatcherCaseDuplicated(self.cases[val])

        self.cases[val] = arm.span

    def unhandled_cases(self) -> Container[bool] | None:
        if WILDCARD in self.cases:
            return None

        cases = list(self.cases)
        assert is_seq_of(cases, bool)

        leftover = {True, False} - set(cases)
        return leftover


class ArrayPatternMatcher:
    def __init__(self) -> None:
        self.cases: dict[tuple[int | Wildcard, ...] | Wildcard, Span] = {}

    def add_case(self, arm: "ArrayPattern | WildcardPattern"):
        from compiler.ast import ArrayPattern, WildcardPattern

        match arm:
            case ArrayPattern():
                val = tuple(arm.pattern_as_list())
            case WildcardPattern():
                val = WILDCARD

        if val in self.cases:
            raise MatcherCaseDuplicated(self.cases[val])

        self.cases[val] = arm.span

    def unhandled_cases(self) -> Container[str] | None:
        if WILDCARD in self.cases:
            return None

        return {"_"}


class EnumPatternMatcher:
    def __init__(self, enum: langtypes.Enum) -> None:
        self.cases: dict[EnumValue | Wildcard, Span] = {}
        self.enum = enum

    def add_case(self, arm: "EnumPattern | WildcardPattern"):
        from compiler.ast import EnumPattern, WildcardPattern

        match arm:
            case EnumPattern():
                val = arm.value
            case WildcardPattern():
                val = WILDCARD

        if val in self.cases:
            raise MatcherCaseDuplicated(self.cases[val])

        self.cases[val] = arm.span

    def unhandled_cases(self) -> Container[str] | None:
        if WILDCARD in self.cases:
            return None

        cases = list(self.cases)
        assert is_seq_of(cases, EnumValue)

        leftover = set(v.name for v in self.enum.members) - set(
            (s.variant for s in cases)
        )
        return leftover


T = TypeVar("T")


def is_seq_of(seq: Sequence[Any], ty: Type[T] | UnionType) -> TypeGuard[Sequence[T]]:
    return all(isinstance(item, ty) for item in seq)
