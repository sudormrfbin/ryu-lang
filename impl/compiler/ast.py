import abc
from typing import Any, Optional, TypeAlias, Union
import typing
import dataclasses
from dataclasses import dataclass
from typing_extensions import override

from lark import Token, ast_utils
from lark.tree import Meta as LarkMeta

from compiler.env import RuntimeEnvironment, TypeEnvironment

from compiler import langtypes, langvalues, runtime
from compiler import errors

_LispAst = list[Union[str, "_LispAst"]]

SKIP_SERIALIZE = "skip_serialize"

# TODO: Narrow down this type
EvalResult = Any

AstDict = dict[typing.Type["_Ast"], dict[str, Any]]

# In AstTypeDict, the key type will always correspond to exactly one value type:
# _Ast -> Type
# str -> AstTypeDict
# Since this cannot be expressed in the type system, we settle for a union type
# which introduces two extra invalid states (_Ast -> AstTypeDict & str -> Type)
AstTypeDict = dict[
    typing.Type["_Ast"] | str,
    typing.Type[langtypes.Type] | "AstTypeDict",
]


# TODO: explain requirement of underscore by lark
@dataclass
class _Ast(abc.ABC, ast_utils.Ast, ast_utils.WithMeta):
    # InitVar makes meta available on the __post_init__ method
    # and excludes it in the generated __init__.
    meta: dataclasses.InitVar[LarkMeta]
    """Line and column numbers from lark framework.
    Converted to Span for strorage within the class."""

    span: errors.Span = dataclasses.field(init=False, metadata={SKIP_SERIALIZE: True})
    """Line and column number information."""

    # kw_only is required to make dataclasses play nice with inheritance and
    # fields with default values. https://stackoverflow.com/a/69822584/7115678
    type_: langtypes.Type | None = dataclasses.field(
        default=None, kw_only=True, metadata={SKIP_SERIALIZE: True}
    )

    def __post_init__(self, meta: LarkMeta):
        self.span = errors.Span.from_meta(meta)

    @abc.abstractmethod
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        pass

    @abc.abstractmethod
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        pass

    def to_dict(self) -> AstDict:
        attrs: dict[str, Any] = {}

        for field in dataclasses.fields(self):
            if SKIP_SERIALIZE in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, _Ast):
                attrs[field.name] = value.to_dict()
            elif isinstance(value, list):
                match value:
                    case []:
                        attrs[field.name] = []
                    case [_Ast(), *_]:  # type: ignore
                        attrs[field.name] = [v.to_dict() for v in value]  # type: ignore
                    case _:  # type: ignore
                        pass
            elif value is not None:
                attrs[field.name] = value

        return {type(self): attrs}

    def to_type_dict(
        self,
    ) -> AstTypeDict:
        assert self.type_ is not None

        result: AstTypeDict = {}
        result[type(self)] = type(self.type_)

        for field in dataclasses.fields(self):
            if SKIP_SERIALIZE in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, _Ast):
                result[field.name] = value.to_type_dict()
            elif isinstance(value, list):
                match value:
                    case []:
                        result[field.name] = []  # type: ignore
                    case [_Ast(), *_]:  # type: ignore
                        result[field.name] = [v.to_type_dict() for v in value]  # type: ignore
                    case _:  # type: ignore
                        pass

        return result


class _Statement(_Ast):
    pass


@dataclass
class StatementList(_Ast, ast_utils.AsList):
    stmts: list[_Statement]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Block:
        types = [stmt.typecheck(env) for stmt in self.stmts]

        self.type_ = langtypes.resolve_blocks_type(types)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        for child in self.stmts:
            child.eval(env)


@dataclass
class StatementBlock(StatementList):
    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Block:
        child_env = TypeEnvironment(enclosing=env)
        return super().typecheck(child_env)

    @override
    def eval(self, env: RuntimeEnvironment):
        child_env = RuntimeEnvironment(enclosing=env)
        return super().eval(child_env)


class _Expression(_Statement):
    pass


@dataclass
class VariableDeclaration(_Statement):
    ident: str
    rvalue: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = self.rvalue.typecheck(env)
        env.define(self.ident, self.type_)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        rhs = self.rvalue.eval(env)
        env.define(self.ident, rhs)


@dataclass
class Assignment(_Statement):
    lvalue: Token
    rvalue: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        lvalue_type = env.get(self.lvalue)
        if lvalue_type is None:
            raise errors.UndeclaredVariable(
                message=f"Variable '{self.lvalue}' not declared in this scope",
                span=errors.Span.from_token(self.lvalue),
                variable=self.lvalue,
                # TODO: Add help message to use let
            )

        rvalue_type = self.rvalue.typecheck(env)
        if lvalue_type != rvalue_type:
            raise errors.InternalCompilerError("Type mismatch: TODO")  # TODO

        self.type_ = rvalue_type
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        rhs = self.rvalue.eval(env)
        env.set(self.lvalue, rhs)


@dataclass
class PrintStmt(_Statement):
    expr: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = self.expr.typecheck(env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        print(self.expr.eval(env))


@dataclass
class IfStmt(_Statement):
    cond: _Expression
    true_block: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Block:
        expr_type = self.cond.typecheck(env)
        if expr_type != langtypes.BOOL:
            raise errors.UnexpectedType(
                message="Unexpected type for if condition",
                span=self.cond.span,
                expected_type=langtypes.BOOL,
                actual_type=expr_type,
            )

        self.type_ = self.true_block.typecheck(env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> bool:
        if self.cond.eval(env) is True:
            self.true_block.eval(env)
            return True

        return False


@dataclass
class IfChain(_Statement):
    if_stmt: IfStmt
    else_if_ladder: Optional["ElseIfLadder"]
    else_block: Optional[StatementBlock]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        types: list[langtypes.Type] = []

        types.append(self.if_stmt.typecheck(env))
        if self.else_block:
            types.append(self.else_block.typecheck(env))
        if self.else_if_ladder:
            types.append(self.else_if_ladder.typecheck(env))

        self.type_ = langtypes.resolve_blocks_type(types)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        if self.if_stmt.eval(env):
            # if condition evaluates to true, stop the if-chain
            return

        if self.else_if_ladder:
            if self.else_if_ladder.eval(env) is True:
                # one of the else-if blocks executed, stop the if-chain
                return

        if self.else_block:
            self.else_block.eval(env)


@dataclass
class ElseIfStmt(IfStmt):
    pass


@dataclass
class ElseIfLadder(_Statement, ast_utils.AsList):
    blocks: list[ElseIfStmt]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        types = [block.typecheck(env) for block in self.blocks]
        self.type_ = langtypes.resolve_blocks_type(types)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> bool:
        """
        Returns True if any of the else if blocks execute.
        """
        for block in self.blocks:
            if block.eval(env) is True:
                return True
        return False


@dataclass
class ArrayPatternElement(_Ast):
    literal: "IntLiteral | WildcardPattern"

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = self.literal.typecheck(env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        return self.literal.eval(env)

    def matches(self, expr: Any) -> bool:
        match self.literal:
            case IntLiteral(value=value):
                return value == expr
            case WildcardPattern():
                return True


@dataclass
class ArrayPattern(_Ast, ast_utils.AsList):
    elements: list[ArrayPatternElement]

    @override
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

        self.type_ = ty
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> list[Any]:
        return [el.eval(env) for el in self.elements]

    def pattern_as_list(self) -> list[int | None]:
        results: list[int | None] = []
        for el in self.elements:
            match el.literal:
                case IntLiteral(value=value):
                    results.append(value)
                case WildcardPattern():
                    results.append(None)
        return results

    def matches(self, expr: list[Any]) -> bool:
        if len(self.elements) != len(expr):
            return False

        return all(pat.matches(e) for pat, e in zip(self.elements, expr))


MatchPattern: TypeAlias = "BoolLiteral | EnumPattern | WildcardPattern | ArrayPattern"


def matches_pattern(pattern: MatchPattern, expr: Any) -> bool:
    match pattern:
        case BoolLiteral():
            return pattern.value == expr
        case EnumPattern():
            assert isinstance(expr, langvalues.EnumValue)
            return pattern.matches(expr)
        case WildcardPattern():
            return True
        case ArrayPattern():
            assert isinstance(expr, list)
            return pattern.matches(expr)  # pyright: ignore [reportUnknownArgumentType]


@dataclass
class EnumPattern(_Expression):
    enum_type: Token
    variant: Token

    @property
    def value(self) -> langvalues.EnumValue:
        return langvalues.EnumValue(ty=self.enum_type, variant=self.variant)

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = env.get(self.enum_type)
        if self.type_ is None:
            raise  # TODO
            # raise errors.UndeclaredType()
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        raise

    def matches(self, expr: langvalues.EnumValue) -> bool:
        return self.value == expr


@dataclass
class CaseStmt(_Ast):
    pattern: MatchPattern
    block: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.block.typecheck(env)
        self.type_ = self.pattern.typecheck(env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        self.block.eval(env)

    def matches(self, expr: Any) -> bool:
        return matches_pattern(self.pattern, expr)


@dataclass
class CaseLadder(_Ast, ast_utils.AsList):
    cases: list[CaseStmt]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        types: list[langtypes.Type] = []
        for case_ in self.cases:
            case_.typecheck(env)
            assert case_.block.type_ is not None
            types.append(case_.block.type_)

        self.type_ = langtypes.resolve_blocks_type(types)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        # eval is handled by match statement
        pass

    def ensure_exhaustive_matching_bool(self, match_stmt: "MatchStmt"):
        seen: dict[bool, BoolLiteral] = {}

        for case_ in self.cases:
            if isinstance(case_.pattern, WildcardPattern):
                # TODO: show warning if there are more cases after wildcard
                return
            assert isinstance(case_.pattern, BoolLiteral)
            pattern = case_.pattern.value

            if pattern in seen:
                raise errors.DuplicatedCase(
                    message="Case condition duplicated",
                    span=case_.pattern.span,
                    previous_case_span=seen[pattern].span,
                )
            seen[pattern] = case_.pattern

        remaining = {True, False} - set(seen)
        if remaining:
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
        variants: list[langtypes.EnumVariantSimple],
        expected_type: langtypes.Type,
    ):
        seen: dict[langvalues.EnumValue, EnumPattern] = {}

        for case_ in self.cases:
            if isinstance(case_.pattern, WildcardPattern):
                # TODO: show warning if there are more cases after wildcard
                return
            assert isinstance(case_.pattern, EnumPattern)
            pattern = case_.pattern.value

            if pattern in seen:
                raise errors.DuplicatedCase(
                    message="Case condition duplicated",
                    span=case_.pattern.span,
                    previous_case_span=seen[pattern].span,
                )
            seen[pattern] = case_.pattern

        remaining = set(v.name for v in variants) - set((s.variant for s in seen))
        if remaining:
            raise errors.InexhaustiveMatch(
                message="Match not exhaustive",
                span=match_stmt.span,
                expected_type=expected_type,
                expected_type_span=match_stmt.expr.span,
                remaining_values=remaining,
            )

    def ensure_exhaustive_matching_array(
        self, match_stmt: "MatchStmt", ty: langtypes.Type
    ):
        seen: dict[tuple[int | None, ...], ArrayPattern] = {}

        for case_ in self.cases:
            if isinstance(case_.pattern, WildcardPattern):
                # TODO: show warning if there are more cases after wildcard
                return
            assert isinstance(case_.pattern, ArrayPattern)
            pattern = case_.pattern.pattern_as_list()

            if tuple(pattern) in seen:
                raise errors.DuplicatedCase(
                    message="Case condition duplicated",
                    span=case_.pattern.span,
                    previous_case_span=seen[tuple(pattern)].span,
                )
            seen[tuple(pattern)] = case_.pattern

        # TODO: separate error for not handling wildcard pattern
        raise errors.InexhaustiveMatch(
            message="Match not exhaustive",
            span=match_stmt.span,
            expected_type=langtypes.Array(ty),
            expected_type_span=match_stmt.expr.span,
            remaining_values={"_"},
        )


@dataclass
class MatchStmt(_Statement):
    expr: _Expression
    cases: CaseLadder

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        expr_type = self.expr.typecheck(env)
        self.type_ = self.cases.typecheck(env)

        for case_ in self.cases.cases:
            case_type = case_.pattern.type_
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
                self.cases.ensure_exhaustive_matching_enum(
                    self,
                    variants=expr_type.members,
                    expected_type=expr_type,
                )
            case langtypes.Array(ty=langtypes.INT):
                self.cases.ensure_exhaustive_matching_array(self, expr_type.ty)
            case _:
                raise errors.InternalCompilerError(
                    "TODO: unsupported type for match expression"
                )

        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        expr = self.expr.eval(env)

        for case_ in self.cases.cases:
            if case_.matches(expr):
                case_.eval(env)
                break
        else:
            raise errors.InternalCompilerError(
                "Match statement did not execute any case blocks"
            )


@dataclass
class WhileStmt(_Statement):
    cond: _Expression
    true_block: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        expr_type = self.cond.typecheck(env)
        if expr_type != langtypes.BOOL:
            raise errors.UnexpectedType(
                message="Unexpected type for while condition",
                span=self.cond.span,
                expected_type=langtypes.BOOL,
                actual_type=expr_type,
            )

        self.type_ = self.true_block.typecheck(env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        while self.cond.eval(env) is True:
            self.true_block.eval(env)


@dataclass
class ForStmt(_Statement):
    var: Token
    arr_name: _Expression
    stmts: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        array_type = self.arr_name.typecheck(env)
        if not isinstance(array_type, langtypes.Array):
            raise errors.UnexpectedType(
                message="Unexpected type",
                span=self.arr_name.span,
                expected_type=langtypes.Array(array_type),
                actual_type=array_type,
            )

        child_env = TypeEnvironment(enclosing=env)
        child_env.define(self.var, array_type.ty)

        self.type_ = self.stmts.typecheck(child_env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        array = self.arr_name.eval(env)
        for element in array:
            loop_env = RuntimeEnvironment(env)
            loop_env.define(self.var, element)
            self.stmts.eval(loop_env)


@dataclass
class ForStmtInt(_Statement):
    var: Token
    start: "IntLiteral"
    end: "IntLiteral"
    stmts: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        start_type = self.start.typecheck(env)
        end_type = self.end.typecheck(env)
        if not isinstance(start_type, langtypes.Int) and not isinstance(
            end_type, langtypes.Int
        ):
            raise  # TODO

        child_env = TypeEnvironment(enclosing=env)
        child_env.define(self.var, start_type)

        self.type_ = self.stmts.typecheck(child_env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        start_index = self.start.eval(env)
        end_index = self.end.eval(env)
        for i in range(start_index, end_index):
            loop_env = RuntimeEnvironment(env)
            loop_env.define(self.var, i)
            self.stmts.eval(loop_env)


@dataclass
class StructMember(_Ast):
    name: Token
    ident_type: "TypeAnnotation"

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = self.ident_type.typecheck(env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        # eval is handled by struct statement
        pass


@dataclass
class StructMembers(_Ast, ast_utils.AsList):
    members: list[StructMember]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Members:
        types = {str(mem.name): mem.typecheck(env) for mem in self.members}
        self.type_ = langtypes.Members(types)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        # eval is handled by struct statement
        pass


@dataclass
class StructStmt(_Ast):
    name: Token
    members: StructMembers

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        if env.get(self.name):
            raise  # TODO
            # raise errors.TypeRedefinition()

        self.type_ = langtypes.Struct(
            struct_name=self.name,
            members=self.members.typecheck(env),
        )
        env.define(self.name, self.type_)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        # Nothing to execute since struct statements are simply declarations
        pass


@dataclass
class StructInitMember(_Ast):
    name: Token
    value: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = self.value.typecheck(env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        return self.value.eval(env)


@dataclass
class StructInitMembers(_Ast, ast_utils.AsList):
    members: list[StructInitMember]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Members:
        types = {str(mem.name): mem.typecheck(env) for mem in self.members}
        self.type_ = langtypes.Members(types)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> dict[str, Any]:
        return {str(mem.name): mem.eval(env) for mem in self.members}


@dataclass
class StructInit(_Ast, ast_utils.AsList):
    name: Token
    members: Optional[StructInitMembers]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Struct:
        struct_type = langtypes.Type.from_str(self.name, env)
        if not isinstance(struct_type, langtypes.Struct):
            raise  # TODO errors.UnexpectedType()

        if self.members:
            members_type = self.members.typecheck(env)
        else:
            members_type = langtypes.Members({})

        mem_len, param_len = len(members_type), len(struct_type.members)
        if mem_len < param_len:
            raise  # TODO insufficient members
        if mem_len > param_len:
            raise  # TODO too many members
        if members_type != struct_type.members:
            raise  # TODO type mismatch

        self.type_ = struct_type
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> langvalues.StructValue:
        return langvalues.StructValue(
            name=self.name,
            attrs=self.members.eval(env) if self.members else {},
        )


@dataclass
class ArrayElement(_Ast):
    element: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = self.element.typecheck(env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        return self.element.eval(env)


@dataclass
class ArrayElements(_Ast, ast_utils.AsList):
    members: list[ArrayElement]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        assert len(self.members) > 0
        check_type = self.members[0].typecheck(env)
        for mem in self.members:
            if mem.typecheck(env) != check_type:
                raise errors.ArrayTypeMismatch(
                    message="Unexpected type for array element",
                    span=mem.span,
                    expected_type=check_type,
                    actual_type=mem.typecheck(env),
                    expected_type_span=self.members[0].span,
                )
        self.type_ = check_type
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        result: list[Any] = []
        for mem in self.members:
            result.append(mem.eval(env))
        return result


@dataclass
class ArrayLiteral(_Ast):
    declared_type: Optional["TypeAnnotation"]
    members: Optional[ArrayElements]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        inferred_type = self.members.typecheck(env) if self.members else None
        declared_type = None
        if self.declared_type:
            declared_type = self.declared_type.typecheck(env)

        match (declared_type, inferred_type):
            case (None, None):
                raise errors.EmptyArrayWithoutTypeAnnotation(
                    message="Empty array without type annonation cannot be declared",
                    span=self.span,
                )
            case (None, infer) if infer is not None:
                self.type_ = langtypes.Array(infer)
            case (decl, None) if decl is not None:
                self.type_ = langtypes.Array(decl)
            case (decl, infer) if decl == infer and decl is not None:
                self.type_ = langtypes.Array(decl)
            case _:
                assert self.members
                assert declared_type
                assert inferred_type
                assert self.declared_type

                raise errors.ArrayTypeMismatch(
                    message="Unexpected type for array element",
                    span=self.members.span,
                    expected_type=declared_type,
                    actual_type=inferred_type,
                    expected_type_span=self.declared_type.span,
                )
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        return self.members.eval(env) if self.members else []


@dataclass
class Indexing(_Ast):
    element: _Expression
    index: int

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = self.element.typecheck(env)
        if not isinstance(self.type_, langtypes.Array):
            raise errors.IndexingNonArray(
                message="indexing non array",
                span=self.element.span,
                actual_type=self.type_,
            )
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        element_value = self.element.eval(env)
        if len(element_value) <= self.index:
            raise errors.IndexingOutOfRange(
                message="Indexing out of range",
                length_array=len(element_value),
                index_value=self.index,
                span=self.span,
            )
        result = element_value[self.index]
        return result


@dataclass
class IndexAssignment(_Ast):
    arrayname: "Variable"
    index: int
    value: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = self.arrayname.typecheck(env)
        value_type = self.value.typecheck(env)
        if not isinstance(self.type_, langtypes.Array):
            raise errors.IndexingNonArray(
                message="indexing non array",
                span=self.arrayname.span,
                actual_type=self.type_,
            )
        if self.type_.ty != value_type:
            raise errors.ArrayIndexAssignmentTypeMismatch(
                message=f"Expected type {self.type_ } but got {value_type}",
                span=self.value.span,
                actual_type=value_type,
                expected_type=self.type_.ty,
                expected_type_span=self.arrayname.span,
            )

        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        array_name = self.arrayname.eval(env)
        array_value = self.value.eval(env)
        array_name[self.index] = array_value
        pass


@dataclass
class EnumMemberBare(_Ast):
    name: Token

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = langtypes.Type()  # TODO: assign separate type
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        # eval is handled by enum statement
        pass


@dataclass
class EnumMemberTuple(_Ast):
    name: Token
    tuple_members: "TypeAnnotation"

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = langtypes.Type()  # TODO: assign separate type

        self.tuple_members.typecheck(env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        # eval is handled by enum statement
        pass


@dataclass
class EnumMembers(_Ast, ast_utils.AsList):
    members: list[EnumMemberBare | EnumMemberTuple]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        seen: dict[Token, EnumMemberBare | EnumMemberTuple] = {}
        for member in self.members:
            if member.name in seen:
                raise errors.DuplicatedAttribute(
                    message="Enum attribute duplicated",
                    span=member.span,
                    previous_case_span=seen[member.name].span,
                )
            seen[member.name] = member
            member.typecheck(env)

        self.type_ = langtypes.BLOCK
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        # eval is handled by enum statement
        pass

    def members_as_list(
        self,
    ) -> list[langtypes.EnumVariantSimple | langtypes.EnumVariantTuple]:
        members: list[langtypes.EnumVariantSimple | langtypes.EnumVariantTuple] = []

        for mem in self.members:
            match mem:
                case EnumMemberBare():
                    members.append(langtypes.EnumVariantSimple(mem.name))
                case EnumMemberTuple():
                    assert mem.tuple_members.type_
                    members.append(
                        langtypes.EnumVariantTuple(
                            mem.name,
                            mem.tuple_members.type_,
                        )
                    )

        return members


@dataclass
class EnumStmt(_Ast):
    name: Token
    members: EnumMembers

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        if isinstance(existing_type := env.get(self.name), langtypes.Enum):
            raise errors.TypeRedefinition(
                message="Enum is redefined",
                type_name=self.name,
                span=errors.Span.from_token(self.name),  # Use the current span
                previous_type_span=existing_type.span,  # Use the stored span
            )
        self.members.typecheck(env)
        self.type_ = langtypes.Enum(
            enum_name=self.name,
            members=self.members.members_as_list(),
            span=errors.Span.from_token(self.name),
        )
        env.define(self.name, self.type_)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        # Nothing to execute since enum statements are simply declarations
        pass


@dataclass
class TypeAnnotation(_Ast):
    ty: Token
    generics: Optional["TypeAnnotation"]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        if self.generics:
            generics = self.generics.typecheck(env)
            self.type_ = langtypes.Type.from_str_with_generics(self.ty, generics, env)
        else:
            self.type_ = langtypes.Type.from_str(self.ty, env)

        if self.type_ is None:
            raise  # TODO
            # raise errors.UnassignableType()
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        pass


@dataclass
class FunctionParam(_Ast):
    name: Token
    arg_type: TypeAnnotation

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = self.arg_type.typecheck(env)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        pass


@dataclass
class FunctionParams(_Ast, ast_utils.AsList):
    args: list[FunctionParam]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Params:
        types = [arg.typecheck(env) for arg in self.args]
        self.type_ = langtypes.Params(types)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        pass

    def param_names(self) -> list[str]:
        return [param.name for param in self.args]


@dataclass
class FunctionDefinition(_Ast):
    name: Token
    args: Optional[FunctionParams]
    return_type: TypeAnnotation
    body: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        ret_type = self.return_type.typecheck(env)
        params = self.args.typecheck(env) if self.args else langtypes.Params([])

        self.type_ = langtypes.Function(
            function_name=self.name,
            arguments=params,
            return_type=ret_type,
        )

        body_env = TypeEnvironment(enclosing=env)
        body_env.define(self.name, self.type_)

        if self.args:
            for arg in self.args.args:
                assert arg.type_ is not None
                body_env.define(arg.name, arg.type_)

        body_block_type = self.body.typecheck(body_env)

        if not isinstance(body_block_type, langtypes.ReturnBlock):
            raise  # TODO

        if body_block_type.return_type != ret_type:
            raise  # TODO

        env.define(self.name, self.type_)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        param_names = self.args.param_names() if self.args else []
        env.define(self.name, langvalues.RyuFunction(param_names, self.body))


@dataclass
class ReturnStmt(_Statement):
    return_value: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        return_type = self.return_value.typecheck(env)

        self.type_ = langtypes.ReturnBlock(return_type, self.span)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        value = self.return_value.eval(env)
        raise runtime.FunctionReturn(value)


@dataclass
class FunctionArgs(_Ast, ast_utils.AsList):
    args: list[_Expression]

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Params:
        types = [arg.typecheck(env) for arg in self.args]
        self.type_ = langtypes.Params(types)
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> list[EvalResult]:
        return [arg.eval(env) for arg in self.args]


@dataclass
class FunctionCall(_Expression):  # TODO: rename to FunctionCallOrStructInit
    callee: _Expression
    args: Optional[FunctionArgs | StructInitMembers]

    is_fn: bool | None = None

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        callee_type = self.callee.typecheck(env)
        args = self.args
        match (callee_type, args):
            case (langtypes.Function(), FunctionArgs() | None):
                self.is_fn = True
                return self.typecheck_function_call(callee_type, args, env)
            case (langtypes.Struct(), StructInitMembers() | None):
                self.is_fn = False
                return self.typecheck_struct_init(callee_type, args, env)
            case _:
                raise  # TODO

    def typecheck_function_call(
        self,
        ty: langtypes.Function,
        args: Optional[FunctionArgs],
        env: TypeEnvironment,
    ):
        if args:
            args_type = args.typecheck(env)
        else:
            args_type = langtypes.Params([])

        arg_len, param_len = len(args_type), len(ty.arguments)
        if arg_len < param_len:
            raise  # TODO insufficient args
        if arg_len > param_len:
            raise  # TODO too many args
        if args_type != ty.arguments:
            raise  # TODO type mismatch

        self.type_ = ty.return_type
        return self.type_

    def typecheck_struct_init(
        self,
        ty: langtypes.Struct,
        members: Optional[StructInitMembers],
        env: TypeEnvironment,
    ):
        if members:
            members_type = members.typecheck(env)
        else:
            members_type = langtypes.Members({})

        mem_len, param_len = len(members_type), len(ty.members)
        if mem_len < param_len:
            raise  # TODO insufficient members
        if mem_len > param_len:
            raise  # TODO too many members
        if members_type != ty.members:
            raise  # TODO type mismatch

        self.type_ = ty
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        if self.is_fn is True:
            return self.eval_function_call(self.callee.eval(env), env)
        elif self.is_fn is False:
            return self.eval_struct_init(env)
        else:
            assert False

    def eval_function_call(
        self, fn: langvalues.Function, env: RuntimeEnvironment
    ) -> Any:
        args = self.args.eval(env) if self.args else []
        assert isinstance(args, list)

        return fn.call(args, env)

    def eval_struct_init(self, env: RuntimeEnvironment) -> langvalues.StructValue:
        assert isinstance(self.args, StructInitMembers)
        assert isinstance(self.type_, langtypes.Struct)

        return langvalues.StructValue(
            name=self.type_.struct_name,
            attrs=self.args.eval(env) if self.args else {},
        )


@dataclass
class Term(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, "+" | "-", langtypes.INT:
                self.type_ = langtypes.INT
            case langtypes.STRING, "+", langtypes.STRING:
                self.type_ = langtypes.STRING
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[
                        errors.OperandSpan(left_type, self.left.span),
                        errors.OperandSpan(right_type, self.right.span),
                    ],
                )

        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case "+":
                return left + right
            case "-":
                return left - right
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class Factor(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, "*" | "/" | "%", langtypes.INT:
                self.type_ = langtypes.INT
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[
                        errors.OperandSpan(left_type, self.left.span),
                        errors.OperandSpan(right_type, self.right.span),
                    ],
                )

        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case "*":
                return left * right
            case "/":
                match self.left.type_, self.right.type_:
                    case langtypes.INT, langtypes.INT:
                        return left // right
                    case _:
                        raise errors.InternalCompilerError(
                            f"{type(self).__name__} recieved invalid operator {self.op}"
                        )
            case "%":
                match self.left.type_, self.right.type_:
                    case langtypes.INT, langtypes.INT:
                        return left % right
                    case _:
                        raise errors.InternalCompilerError(
                            f"{type(self).__name__} recieved invalid operator {self.op}"
                        )
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class Comparison(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, ">" | "<" | "<=" | ">=", langtypes.INT:
                self.type_ = langtypes.BOOL
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[
                        errors.OperandSpan(left_type, self.left.span),
                        errors.OperandSpan(right_type, self.right.span),
                    ],
                )

        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case ">":
                return left > right
            case "<":
                return left < right
            case "<=":
                return left <= right
            case ">=":
                return left >= right
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class Logical(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.BOOL, "&&", langtypes.BOOL:
                self.type_ = langtypes.BOOL
            case langtypes.BOOL, "||", langtypes.BOOL:
                self.type_ = langtypes.BOOL
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[
                        errors.OperandSpan(left_type, self.left.span),
                        errors.OperandSpan(right_type, self.right.span),
                    ],
                )

        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case "&&":
                return left and right
            case "||":
                return left or right
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class Equality(_Expression):
    left: _Expression
    op: Token
    right: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        if left_type == right_type and self.op in ("==", "!="):  # pyright: ignore [reportUnnecessaryContains]
            self.type_ = langtypes.BOOL
        else:
            op_span = errors.Span.from_token(self.op)
            raise errors.InvalidOperationError(
                message=f"Invalid operation {self.op} for types {left_type.name} and {right_type.name}",
                span=self.span,
                operator=errors.OperatorSpan(self.op, op_span),
                operands=[
                    errors.OperandSpan(left_type, self.left.span),
                    errors.OperandSpan(right_type, self.right.span),
                ],
            )

        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case "==":
                return left == right
            case "!=":
                return left != right
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class UnaryOp(_Expression):
    op: Token
    operand: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        operand_type = self.operand.typecheck(env)

        match self.op, operand_type:
            case "+" | "-", langtypes.INT:
                self.type_ = operand_type
            case "!", langtypes.BOOL:
                self.type_ = operand_type
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation '{self.op}' for type '{operand_type.name}'",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[errors.OperandSpan(operand_type, self.operand.span)],
                )

        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        result = self.operand.eval(env)
        match self.op:
            case "+":
                return result
            case "-":
                return -result
            case "!":
                return not result
            case _:
                raise errors.InternalCompilerError(
                    f"{type(self).__name__} recieved invalid operator {self.op}"
                )


@dataclass
class BoolLiteral(_Expression):
    value: bool

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = langtypes.BOOL
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class IntLiteral(_Expression):
    value: int

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = langtypes.INT
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class StringLiteral(_Expression):
    value: str

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = langtypes.STRING
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class EnumLiteralSimple(_Expression):
    enum_type: Token
    variant: Token

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = env.get(self.enum_type)
        if self.type_ is None:
            raise  # TODO
            # raise errors.UndeclaredType()
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> langvalues.EnumValue:
        return langvalues.EnumValue(ty=self.enum_type, variant=self.variant)


@dataclass
class EnumLiteralTuple(_Expression):
    enum_type: Token
    variant: Token
    inner: _Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = env.get(self.enum_type)
        if self.type_ is None:
            raise  # TODO
            # raise errors.UndeclaredType()
        if not isinstance(self.type_, langtypes.Enum):
            raise  # TODO

        inner_type = self.inner.typecheck(env)
        variant_type = self.type_.variant_from_str(self.variant)
        if not isinstance(variant_type, langtypes.EnumVariantTuple):
            raise  # TODO

        if variant_type.inner != inner_type:
            raise  # TODO

        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        return langvalues.EnumTupleValue(
            ty=self.enum_type,
            variant=self.variant,
            tuple_value=self.inner.eval(env),
        )


@dataclass
class Variable(_Expression):
    value: str

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = env.get(self.value)
        if self.type_ is None:
            raise errors.UnknownVariable(
                message=f"Variable '{self.value}' not declared in this scope",
                span=self.span,
                variable=self.value,
            )
        else:
            return self.type_

    @override
    def eval(self, env: RuntimeEnvironment):
        return env.get(self.value)


class WildcardPattern(_Ast):
    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type_ = langtypes.PLACEHOLDER
        return self.type_

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        pass
