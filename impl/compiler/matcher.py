from dataclasses import dataclass
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Any,
    Container,
    Optional,
    Sequence,
    Type,
    TypeAlias,
    TypeGuard,
    TypeVar,
)

from compiler import errors, langtypes
from compiler.langvalues import EnumValue


if TYPE_CHECKING:
    from compiler.ast import EnumPatternTuple
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


@dataclass
class _EnumVariant:
    name: str
    inner: "Optional[BoolPatternMatcher | ArrayPatternMatcher | EnumPatternMatcher]"


Matcher: TypeAlias = "BoolPatternMatcher | ArrayPatternMatcher | EnumPatternMatcher"


class EnumPatternMatcher:
    def __init__(self, enum: langtypes.Enum) -> None:
        self.cases: dict[str | Wildcard, tuple[Span, Optional[Matcher]]] = {}
        self.enum = enum

    def add_case(self, arm: "EnumPattern | EnumPatternTuple | WildcardPattern"):
        from compiler.ast import (
            EnumPattern,
            WildcardPattern,
            EnumPatternTuple,
            BoolLiteral,
            ArrayPattern,
        )

        match arm:
            case EnumPattern():
                val = arm.variant
            case WildcardPattern():
                val = WILDCARD

        if val in self.cases:
            matcher = self.cases[val][1]
            if matcher is None:
                raise MatcherCaseDuplicated(self.cases[val][0])
            elif matcher and isinstance(arm, EnumPatternTuple):
                matcher.add_case(arm.tuple_pattern)  # type: ignore
            else:
                raise errors.InternalCompilerError()
        else:
            if isinstance(arm, EnumPatternTuple):
                match arm.tuple_pattern:
                    case BoolLiteral():
                        matcher = BoolPatternMatcher()
                        matcher.add_case(arm.tuple_pattern)
                    case ArrayPattern():
                        matcher = ArrayPatternMatcher()
                        matcher.add_case(arm.tuple_pattern)
                    case EnumPattern():
                        # matcher = EnumPatternMatcher()
                        raise NotImplementedError()
                    case WildcardPattern():
                        matcher = BoolPatternMatcher()  # any matcher is fine here
                        matcher.add_case(arm.tuple_pattern)
                self.cases[val] = (arm.span, matcher)
            else:
                self.cases[val] = (arm.span, None)

    def unhandled_cases(self) -> Container[str] | None:
        if WILDCARD in self.cases:
            return None

        leftover: set[str] = set()
        for variant, span_and_matcher in self.cases.items():
            _, matcher = span_and_matcher
            if matcher is None:
                continue
            if remaining := matcher.unhandled_cases():
                for rem in remaining:  # type: ignore
                    leftover.add(f"{self.enum.name}::{variant}({rem})")

        return leftover if leftover else None


T = TypeVar("T")


def is_seq_of(seq: Sequence[Any], ty: Type[T] | UnionType) -> TypeGuard[Sequence[T]]:
    return all(isinstance(item, ty) for item in seq)
