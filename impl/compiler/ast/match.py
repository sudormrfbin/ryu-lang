from typing import Any, TypeAlias
from compiler import errors, langtypes, langvalues
from compiler.ast.expressions import Expression
from compiler.ast.literals import BoolLiteral, IntLiteral
from compiler.ast.statements import Statement, StatementBlock
from compiler.env import RuntimeEnvironment, TypeEnvironment


from dataclasses import dataclass
from typing_extensions import override

from compiler.ast.base import Ast
from compiler.lalr import Token
from compiler.matcher import (
    WILDCARD,
    ArrayPatternMatcher,
    BoolPatternMatcher,
    EnumPatternMatcher,
    MatcherCaseDuplicated,
    Wildcard,
)


class WildcardPattern(Ast):
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.PLACEHOLDER
        return self.type

    def eval(self, env: RuntimeEnvironment):
        pass  # TODO: remove


@dataclass
class ArrayPatternElement(Ast):
    literal: "IntLiteral | WildcardPattern"

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = self.literal.typecheck(env)
        return self.type

    def eval(self, env: RuntimeEnvironment) -> Any:
        return self.literal.eval(env)

    def matches(self, expr: Any) -> bool:
        match self.literal:
            case IntLiteral(value=value):
                return value == expr
            case WildcardPattern():
                return True


@dataclass
class ArrayPattern(Ast):
    elements: list[ArrayPatternElement]

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        ty = langtypes.UntypedArray()

        for el in self.elements:
            el_type = el.typecheck(env)
            match (ty, el.literal):
                case (_, WildcardPattern()):
                    pass  # type stays the same
                case (langtypes.UntypedArray(), _):
                    ty = langtypes.Array(el_type)
                case (_, _) if el_type == ty.ty:
                    pass
                case _:
                    raise  # TODO

        self.type = ty
        return self.type

    def eval(self, env: RuntimeEnvironment) -> list[Any]:
        return [el.eval(env) for el in self.elements]

    def pattern_as_list(self) -> list[int | Wildcard]:
        results: list[int | Wildcard] = []
        for el in self.elements:
            match el.literal:
                case IntLiteral(value=value):
                    results.append(value)
                case WildcardPattern():
                    results.append(WILDCARD)
        return results

    def matches(self, expr: list[Any]) -> bool:
        if len(self.elements) != len(expr):
            return False

        return all(pat.matches(e) for pat, e in zip(self.elements, expr))


MatchPattern: TypeAlias = (
    "BoolLiteral | EnumPattern | EnumPatternTuple | WildcardPattern | ArrayPattern"
)


def matches_pattern(pattern: MatchPattern, expr: Any) -> bool:
    match pattern:
        case BoolLiteral():
            return pattern.value == expr
        case EnumPatternTuple():
            if isinstance(expr, langvalues.EnumTupleValue):
                return pattern.matches(expr)
            else:
                return False
        case EnumPattern():
            assert isinstance(expr, langvalues.EnumValue)
            return pattern.matches(expr)
        case WildcardPattern():
            return True
        case ArrayPattern():
            assert isinstance(expr, list)
            return pattern.matches(expr)  # pyright: ignore [reportUnknownArgumentType]


@dataclass
class EnumPattern(Expression):
    enum_type: Token
    variant: Token

    @property
    def value(self) -> langvalues.EnumValue:
        return langvalues.EnumValue(ty=self.enum_type, variant=self.variant)

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = env.get_type(self.enum_type)
        if self.type is None:
            raise  # TODO
            # raise errors.UndeclaredType()
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        raise

    def matches(self, expr: langvalues.EnumValue) -> bool:
        return self.value == expr


@dataclass
class EnumPatternTuple(EnumPattern):
    tuple_pattern: MatchPattern

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.tuple_pattern.typecheck(env)
        return super().typecheck(env)

    @override
    def matches(self, expr: langvalues.EnumTupleValue) -> bool:  # type: ignore
        if self.enum_type != expr.ty or self.variant != expr.variant:
            return False
        return matches_pattern(self.tuple_pattern, expr.tuple_value)


@dataclass
class CaseStmt(Ast):
    pattern: MatchPattern
    block: StatementBlock

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.block.typecheck(env)
        self.type = self.pattern.typecheck(env)
        return self.type

    def eval(self, env: RuntimeEnvironment) -> Any:
        self.block.eval(env)

    def matches(self, expr: Any) -> bool:
        return matches_pattern(self.pattern, expr)


@dataclass
class CaseLadder(Ast):
    cases: list[CaseStmt]

    def typecheck(self, env: TypeEnvironment):
        for case_ in self.cases:
            case_.typecheck(env)

    def ensure_exhaustive_matching_bool(self, match_stmt: "MatchStmt"):
        matcher = BoolPatternMatcher()

        for case in self.cases:
            assert isinstance(pat := case.pattern, WildcardPattern | BoolLiteral)
            try:
                matcher.add_case(pat)
            except MatcherCaseDuplicated as e:
                raise errors.DuplicatedCase(
                    message="Case condition duplicated",
                    span=pat.span,
                    previous_case_span=e.previous_case_span,
                )

        if remaining := matcher.unhandled_cases():
            raise errors.InexhaustiveMatch(
                message="Match not exhaustive",
                span=match_stmt.span,
                expected_type=langtypes.BOOL,
                expected_type_span=match_stmt.expr.span,
                remaining_values=remaining,
            )

    def ensure_exhaustive_matching_enum(
        self,
        match_stmt: "MatchStmt",
        enum_type: langtypes.Enum,
    ):
        matcher = EnumPatternMatcher(enum_type)

        for case in self.cases:
            assert isinstance(pat := case.pattern, WildcardPattern | EnumPattern)
            try:
                matcher.add_case(pat)
            except MatcherCaseDuplicated as e:
                raise errors.DuplicatedCase(
                    message="Case condition duplicated",
                    span=pat.span,
                    previous_case_span=e.previous_case_span,
                )

        if remaining := matcher.unhandled_cases():
            raise errors.InexhaustiveMatch(
                message="Match not exhaustive",
                span=match_stmt.span,
                expected_type=enum_type,
                expected_type_span=match_stmt.expr.span,
                remaining_values=remaining,
            )

    def ensure_exhaustive_matching_array(
        self, match_stmt: "MatchStmt", ty: langtypes.Type
    ):
        matcher = ArrayPatternMatcher()

        for case in self.cases:
            assert isinstance(pat := case.pattern, WildcardPattern | ArrayPattern)
            try:
                matcher.add_case(pat)
            except MatcherCaseDuplicated as e:
                raise errors.DuplicatedCase(
                    message="Case condition duplicated",
                    span=pat.span,
                    previous_case_span=e.previous_case_span,
                )

        if remaining := matcher.unhandled_cases():
            raise errors.InexhaustiveMatch(
                message="Match not exhaustive",
                span=match_stmt.span,
                expected_type=langtypes.Array(ty),
                expected_type_span=match_stmt.expr.span,
                remaining_values=remaining,
            )


@dataclass
class MatchStmt(Statement):
    expr: Expression
    cases: CaseLadder

    @override
    def typecheck(self, env: TypeEnvironment):
        expr_type = self.expr.typecheck(env)
        self.cases.typecheck(env)

        for case_ in self.cases.cases:
            case_type = case_.pattern.type
            assert case_type is not None

            if isinstance(case_.pattern, WildcardPattern):
                continue

            if case_type == expr_type:
                continue

            case_is_untyped_array = isinstance(case_type, langtypes.UntypedArray)
            expr_is_array = isinstance(expr_type, langtypes.Array)
            if case_is_untyped_array and expr_is_array:
                continue

            # TODO: Add spanshot test when adding more types of patterns
            raise errors.TypeMismatch(
                message=f"Expected type {expr_type} but got {case_type}",
                span=case_.pattern.span,
                actual_type=case_type,
                expected_type=expr_type,
                expected_type_span=self.expr.span,
            )

        match expr_type:
            case langtypes.BOOL:
                self.cases.ensure_exhaustive_matching_bool(self)
            case langtypes.Enum():
                self.cases.ensure_exhaustive_matching_enum(self, enum_type=expr_type)
            case langtypes.Array(ty=langtypes.INT):
                self.cases.ensure_exhaustive_matching_array(self, expr_type.ty)
            case _:
                raise errors.InternalCompilerError(
                    "TODO: unsupported type for match expression"
                )

    @override
    def eval(self, env: RuntimeEnvironment) -> Any:
        expr = self.expr.eval(env)

        for case_ in self.cases.cases:
            if case_.matches(expr):
                case_.eval(env)
                break
        else:
            raise errors.InternalCompilerError(
                "Match statement did not execute any case blocks"
            )
