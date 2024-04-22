import abc
from typing import Any, Optional, TypeAlias
import typing
import dataclasses
from dataclasses import dataclass
from typing_extensions import override

from lark import Token
from lark.tree import Meta as LarkMeta

from compiler.env import FunctionDefScope, RuntimeEnvironment, TypeEnvironment

from compiler import langtypes, langvalues, runtime
from compiler import errors
from compiler.matcher import (
    WILDCARD,
    ArrayPatternMatcher,
    BoolPatternMatcher,
    EnumPatternMatcher,
    MatcherCaseDuplicated,
    Wildcard,
)


SKIP_SERIALIZE = "skip_serialize"

# TODO: Narrow down this type
EvalResult = Any

AstDict = dict[typing.Type["Ast"], dict[str, Any]]


@dataclass
class Ast(abc.ABC):
    # InitVar makes meta available on the __post_init__ method
    # and excludes it in the generated __init__.
    meta: dataclasses.InitVar[LarkMeta]
    """Line and column numbers from lark framework.
    Converted to Span for strorage within the class."""

    span: errors.Span = dataclasses.field(init=False, metadata={SKIP_SERIALIZE: True})
    """Line and column number information."""

    def __post_init__(self, meta: LarkMeta):
        self.span = errors.Span.from_meta(meta)

    def to_dict(self) -> AstDict:
        attrs: dict[str, Any] = {}

        for field in dataclasses.fields(self):
            if SKIP_SERIALIZE in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, Ast):
                attrs[field.name] = value.to_dict()
            elif isinstance(value, list):
                match value:
                    case []:
                        attrs[field.name] = []
                    case [Ast(), *_]:  # type: ignore
                        attrs[field.name] = [v.to_dict() for v in value]  # type: ignore
                    case _:  # type: ignore
                        pass
            elif value is not None:
                attrs[field.name] = value

        return {type(self): attrs}

    def to_type_dict(self) -> dict[Any, Any]:
        attrs = {}

        if ty := getattr(self, "type", None):
            attrs["type"] = type(ty)

        fields = attrs["fields"] = {}

        for field in dataclasses.fields(self):
            if SKIP_SERIALIZE in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, Ast):
                fields[field.name] = value.to_type_dict()
            elif isinstance(value, list):
                match value:
                    case []:
                        fields[field.name] = []
                    case [Ast(), *_]:  # type: ignore
                        fields[field.name] = [v.to_type_dict() for v in value]  # type: ignore
                    case _:  # type: ignore
                        pass

        return {type(self): attrs}


class Statement(Ast):
    @abc.abstractmethod
    def typecheck(self, env: TypeEnvironment):
        pass

    @abc.abstractmethod
    def eval(self, env: RuntimeEnvironment):
        pass


@dataclass
class StatementList(Ast):
    stmts: list[Statement]

    def typecheck(self, env: TypeEnvironment):
        for stmt in self.stmts:
            stmt.typecheck(env)

    def eval(self, env: RuntimeEnvironment):
        for child in self.stmts:
            child.eval(env)


@dataclass
class StatementBlock(StatementList):
    @override
    def typecheck(self, env: TypeEnvironment):
        child_env = TypeEnvironment(enclosing=env)
        super().typecheck(child_env)

    @override
    def eval(self, env: RuntimeEnvironment):
        child_env = RuntimeEnvironment(enclosing=env)
        return super().eval(child_env)


@dataclass
class Expression(Ast):
    # kw_only is required to make dataclasses play nice with inheritance and
    # fields with default values. https://stackoverflow.com/a/69822584/7115678
    type: langtypes.Type | None = dataclasses.field(
        default=None,
        kw_only=True,
    )

    @abc.abstractmethod
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        pass

    @abc.abstractmethod
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        pass


@dataclass
class VariableDeclaration(Statement):
    ident: str
    rvalue: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        ty = self.rvalue.typecheck(env)
        env.define_var_type(self.ident, ty)

    @override
    def eval(self, env: RuntimeEnvironment):
        rhs = self.rvalue.eval(env)
        env.define(self.ident, rhs)


@dataclass
class Assignment(Statement):
    lvalue: Token
    rvalue: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        lvalue_type = env.get_var_type(self.lvalue)
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

    @override
    def eval(self, env: RuntimeEnvironment):
        rhs = self.rvalue.eval(env)
        env.set(self.lvalue, rhs)


@dataclass
class PrintStmt(Statement):
    expr: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        self.expr.typecheck(env)

    @override
    def eval(self, env: RuntimeEnvironment):
        print(self.expr.eval(env))


@dataclass
class IfStmt(Ast):
    cond: Expression
    true_block: StatementBlock

    def typecheck(self, env: TypeEnvironment):
        expr_type = self.cond.typecheck(env)
        if expr_type != langtypes.BOOL:
            raise errors.UnexpectedType(
                message="Unexpected type for if condition",
                span=self.cond.span,
                expected_type=langtypes.BOOL,
                actual_type=expr_type,
            )

        self.true_block.typecheck(env)

    def eval(self, env: RuntimeEnvironment) -> bool:
        if self.cond.eval(env) is True:
            self.true_block.eval(env)
            return True

        return False


@dataclass
class IfChain(Statement):
    if_stmt: IfStmt
    else_if_ladder: Optional["ElseIfLadder"]
    else_block: Optional[StatementBlock]

    @override
    def typecheck(self, env: TypeEnvironment):
        self.if_stmt.typecheck(env)
        if self.else_block:
            self.else_block.typecheck(env)
        if self.else_if_ladder:
            self.else_if_ladder.typecheck(env)

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
class ElseIfLadder(Ast):
    blocks: list[ElseIfStmt]

    def typecheck(self, env: TypeEnvironment):
        for block in self.blocks:
            block.typecheck(env)

    def eval(self, env: RuntimeEnvironment) -> bool:
        """
        Returns True if any of the else if blocks execute.
        """
        for block in self.blocks:
            if block.eval(env) is True:
                return True
        return False


@dataclass
class ArrayPatternElement(Ast):
    literal: "IntLiteral | WildcardPattern"

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = self.literal.typecheck(env)
        return self.type

    def eval(self, env: RuntimeEnvironment) -> EvalResult:
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

    def eval(self, env: RuntimeEnvironment) -> EvalResult:
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
class WhileStmt(Statement):
    cond: Expression
    true_block: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment):
        expr_type = self.cond.typecheck(env)
        if expr_type != langtypes.BOOL:
            raise errors.UnexpectedType(
                message="Unexpected type for while condition",
                span=self.cond.span,
                expected_type=langtypes.BOOL,
                actual_type=expr_type,
            )

        self.true_block.typecheck(env)

    @override
    def eval(self, env: RuntimeEnvironment):
        while self.cond.eval(env) is True:
            self.true_block.eval(env)


@dataclass
class ForStmt(Statement):
    var: Token
    arr_name: Expression
    stmts: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment):
        array_type = self.arr_name.typecheck(env)
        if not isinstance(array_type, langtypes.Array) and not isinstance(
            array_type, langtypes.String
        ):
            raise errors.UnexpectedType(
                message="Unexpected type",
                span=self.arr_name.span,
                expected_type=langtypes.Array(array_type),
                actual_type=array_type,
            )

        child_env = TypeEnvironment(enclosing=env)
        child_env.define_var_type(self.var, array_type)

        self.stmts.typecheck(child_env)

    @override
    def eval(self, env: RuntimeEnvironment):
        array = self.arr_name.eval(env)
        for element in array:
            loop_env = RuntimeEnvironment(env)
            loop_env.define(self.var, element)
            self.stmts.eval(loop_env)


@dataclass
class ForStmtInt(Statement):
    var: Token
    start: Expression
    end: Expression
    stmts: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment):
        start_type = self.start.typecheck(env)
        end_type = self.end.typecheck(env)
        if not isinstance(start_type, langtypes.Int) and not isinstance(
            end_type, langtypes.Int
        ):
            raise  # TODO

        child_env = TypeEnvironment(enclosing=env)
        child_env.define_var_type(self.var, start_type)

        self.stmts.typecheck(child_env)

    @override
    def eval(self, env: RuntimeEnvironment):
        start_index = self.start.eval(env)
        end_index = self.end.eval(env)
        for i in range(start_index, end_index):
            loop_env = RuntimeEnvironment(env)
            loop_env.define(self.var, i)
            self.stmts.eval(loop_env)


@dataclass
class StructMember(Ast):
    name: Token
    ident_type: "TypeAnnotation"

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = self.ident_type.typecheck(env)
        return self.type


@dataclass
class StructMembers(Ast):
    members: list[StructMember]

    def typecheck(self, env: TypeEnvironment) -> langtypes.Struct.Members:
        types = {str(mem.name): mem.typecheck(env) for mem in self.members}
        self.type = langtypes.Struct.Members(types)
        return self.type


@dataclass
class StructStmt(Statement):
    name: Token
    members: StructMembers

    @override
    def typecheck(self, env: TypeEnvironment):
        if env.get_type(self.name):
            raise  # TODO
            # raise errors.TypeRedefinition()

        ty = langtypes.Struct(
            struct_name=self.name,
            members=self.members.typecheck(env),
        )
        env.define_type(self.name, ty)

    @override
    def eval(self, env: RuntimeEnvironment):
        # Nothing to execute since struct statements are simply declarations
        pass


@dataclass
class StructInitMember(Ast):
    name: Token
    value: Expression

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = self.value.typecheck(env)
        return self.type

    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        return self.value.eval(env)


@dataclass
class StructInitMembers(Ast):
    members: list[StructInitMember]

    def typecheck(self, env: TypeEnvironment) -> langtypes.Struct.Members:
        types = {str(mem.name): mem.typecheck(env) for mem in self.members}
        self.type = langtypes.Struct.Members(types)
        return self.type

    def eval(self, env: RuntimeEnvironment) -> dict[str, Any]:
        return {str(mem.name): mem.eval(env) for mem in self.members}


@dataclass
class StructInit(Ast):
    name: Token
    members: Optional[StructInitMembers]

    def typecheck(self, env: TypeEnvironment) -> langtypes.Struct:
        struct_type = env.get_type(self.name)
        if not isinstance(struct_type, langtypes.Struct):
            raise  # TODO errors.UnexpectedType()

        if self.members:
            members_type = self.members.typecheck(env)
        else:
            members_type = langtypes.Struct.Members({})

        mem_len, param_len = len(members_type), len(struct_type.members)
        if mem_len < param_len:
            raise  # TODO insufficient members
        if mem_len > param_len:
            raise  # TODO too many members
        if members_type != struct_type.members:
            raise  # TODO type mismatch

        self.type = struct_type
        return self.type

    def eval(self, env: RuntimeEnvironment) -> langvalues.StructValue:
        return langvalues.StructValue(
            name=self.name,
            attrs=self.members.eval(env) if self.members else {},
        )


@dataclass
class StructAccess(Statement):  # TODO: make an expression
    name: Token
    member: Token

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:  # type: ignore
        struct_type = env.get_var_type(self.name)
        if not isinstance(struct_type, langtypes.Struct):
            raise  # TODO

        member_type = struct_type.members.types.get(self.member)
        if member_type is None:
            raise  # TODO

        self.type = member_type
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        struct_value = env.get(self.name)
        return struct_value.get_attr(self.member)


@dataclass
class StructAssignment(Statement):
    struct_access: StructAccess
    value: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        member_type = self.struct_access.typecheck(env)
        value_type = self.value.typecheck(env)

        if value_type != member_type:
            raise errors.TypeMismatch(
                message=f"Expected type '{member_type.name}' but got '{value_type.name}'",
                span=self.value.span,
                actual_type=value_type,
                expected_type=member_type,
                expected_type_span=self.struct_access.span,
            )

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        struct_value = env.get(self.struct_access.name)
        value = self.value.eval(env)
        struct_value.set_attr(str(self.struct_access.member), value)


@dataclass
class ArrayElement(Ast):
    element: Expression

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = self.element.typecheck(env)
        return self.type

    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        return self.element.eval(env)


@dataclass
class ArrayElements(Ast):
    members: list[ArrayElement]

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
        self.type = check_type
        return self.type

    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        result: list[Any] = []
        for mem in self.members:
            result.append(mem.eval(env))
        return result


@dataclass
class ArrayLiteral(Ast):
    declared_type: Optional["TypeAnnotation"]
    members: Optional[ArrayElements]

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
                self.type = langtypes.Array(infer)
            case (decl, None) if decl is not None:
                self.type = langtypes.Array(decl)
            case (decl, infer) if decl == infer and decl is not None:
                self.type = langtypes.Array(decl)
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
        return self.type

    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        return self.members.eval(env) if self.members else []


@dataclass
class Indexing(Ast):
    element: Expression
    index: Expression

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        array_type = self.element.typecheck(env)
        index_type = self.index.typecheck(env)
        if not isinstance(array_type, langtypes.Array):
            raise errors.IndexingNonArray(
                message="indexing non array",
                span=self.element.span,
                actual_type=array_type,
            )
        if not isinstance(index_type, langtypes.Int):
            raise  # TODO

        self.type = array_type.ty
        return self.type

    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        element_value = self.element.eval(env)
        array_ind = self.index.eval(env)
        if len(element_value) <= array_ind:
            raise errors.IndexingOutOfRange(
                message="Indexing out of range",
                length_array=len(element_value),
                index_value=array_ind,
                span=self.span,
            )
        result = element_value[array_ind]
        return result


@dataclass
class IndexAssignment(Statement):
    arrayname: "Variable"
    index: Expression
    value: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        index_type = self.index.typecheck(env)
        type = self.arrayname.typecheck(env)
        value_type = self.value.typecheck(env)
        if not isinstance(type, langtypes.Array):
            raise errors.IndexingNonArray(
                message="indexing non array",
                span=self.arrayname.span,
                actual_type=type,
            )

        if not isinstance(index_type, langtypes.Int):
            raise  # TODO

        if type.ty != value_type:
            raise errors.ArrayIndexAssignmentTypeMismatch(
                message=f"Expected type {type } but got {value_type}",
                span=self.value.span,
                actual_type=value_type,
                expected_type=type.ty,
                expected_type_span=self.arrayname.span,
            )

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        array_name = self.arrayname.eval(env)
        array_value = self.value.eval(env)
        array_index = self.index.eval(env)
        array_name[array_index] = array_value


@dataclass
class EnumMemberBare(Ast):
    name: Token

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.Type()  # TODO: assign separate type
        return self.type


@dataclass
class EnumMemberTuple(Ast):
    name: Token
    tuple_members: "TypeAnnotation"

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.Type()  # TODO: assign separate type

        self.tuple_members.typecheck(env)
        return self.type


@dataclass
class EnumMembers(Ast):
    members: list[EnumMemberBare | EnumMemberTuple]

    def typecheck(self, env: TypeEnvironment):
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

    def members_as_list(
        self,
    ) -> list[langtypes.Enum.Variants]:
        members: list[langtypes.Enum.Variants] = []

        for mem in self.members:
            match mem:
                case EnumMemberBare():
                    members.append(langtypes.Enum.Simple(mem.name))
                case EnumMemberTuple():
                    assert mem.tuple_members.type
                    members.append(
                        langtypes.Enum.Tuple(
                            mem.name,
                            mem.tuple_members.type,
                        )
                    )

        return members


@dataclass
class EnumStmt(Statement):
    name: Token
    members: EnumMembers

    @override
    def typecheck(self, env: TypeEnvironment):
        if isinstance(existing_type := env.get_type(self.name), langtypes.Enum):
            raise errors.TypeRedefinition(
                message="Enum is redefined",
                type_name=self.name,
                span=errors.Span.from_token(self.name),  # Use the current span
                previous_type_span=existing_type.span,  # Use the stored span
            )
        self.members.typecheck(env)
        ty = langtypes.Enum(
            enum_name=self.name,
            members=self.members.members_as_list(),
            span=errors.Span.from_token(self.name),
        )
        env.define_type(self.name, ty)

    @override
    def eval(self, env: RuntimeEnvironment):
        # Nothing to execute since enum statements are simply declarations
        pass


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


@dataclass
class FunctionParam(Ast):
    name: Token
    arg_type: TypeAnnotation

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = self.arg_type.typecheck(env)
        return self.type


@dataclass
class FunctionParams(Ast):
    args: list[FunctionParam]

    def typecheck(self, env: TypeEnvironment) -> langtypes.Function.Params:
        types = [arg.typecheck(env) for arg in self.args]
        self.type = langtypes.Function.Params(types)
        return self.type

    def param_names(self) -> list[str]:
        return [param.name for param in self.args]


@dataclass
class FunctionDefinition(Statement):
    name: Token
    args: Optional[FunctionParams]
    return_type: TypeAnnotation
    body: StatementBlock

    @override
    def typecheck(self, env: TypeEnvironment):
        ret_type = self.return_type.typecheck(env)
        params = (
            self.args.typecheck(env) if self.args else langtypes.Function.Params([])
        )

        type = langtypes.Function(
            function_name=self.name,
            arguments=params,
            return_type=ret_type,
        )

        body_env = TypeEnvironment(enclosing=env, fn_scope=FunctionDefScope(ret_type))
        body_env.define_var_type(self.name, type)

        if self.args:
            for arg in self.args.args:
                assert arg.type is not None
                body_env.define_var_type(arg.name, arg.type)

        self.body.typecheck(body_env)

        env.define_var_type(self.name, type)

    @override
    def eval(self, env: RuntimeEnvironment) -> EvalResult:
        param_names = self.args.param_names() if self.args else []
        env.define(self.name, langvalues.RyuFunction(param_names, self.body))


@dataclass
class ReturnStmt(Statement):
    return_value: Expression

    @override
    def typecheck(self, env: TypeEnvironment):
        return_type = self.return_value.typecheck(env)
        if return_type != env.fn_return_type():
            raise  # TODO

    @override
    def eval(self, env: RuntimeEnvironment):
        value = self.return_value.eval(env)
        raise runtime.FunctionReturn(value)


@dataclass
class FunctionArgs(Ast):
    args: list[Expression]

    def typecheck(self, env: TypeEnvironment) -> langtypes.Function.Params:
        types = [arg.typecheck(env) for arg in self.args]
        self.type = langtypes.Function.Params(types)
        return self.type

    def eval(self, env: RuntimeEnvironment) -> list[EvalResult]:
        return [arg.eval(env) for arg in self.args]


@dataclass
class FunctionCall(Expression):  # TODO: rename to FunctionCallOrStructInit
    callee: "Variable"
    args: Optional[FunctionArgs | StructInitMembers]

    is_fn: bool | None = None

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.callee.type = ctype = env.get_var_type(self.callee.value) or env.get_type(
            self.callee.value
        )
        args = self.args
        match (ctype, args):
            case (langtypes.Function(), FunctionArgs() | None):
                self.is_fn = True
                return self.typecheck_function_call(ctype, args, env)
            case (langtypes.Struct(), StructInitMembers() | None):
                self.is_fn = False
                return self.typecheck_struct_init(ctype, args, env)
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
            args_type = langtypes.Function.Params([])

        arg_len, param_len = len(args_type), len(ty.arguments)
        if arg_len < param_len:
            raise  # TODO insufficient args
        if arg_len > param_len:
            raise  # TODO too many args
        if args_type != ty.arguments:
            raise  # TODO type mismatch

        self.type = ty.return_type
        return self.type

    def typecheck_struct_init(
        self,
        ty: langtypes.Struct,
        members: Optional[StructInitMembers],
        env: TypeEnvironment,
    ):
        if members:
            members_type = members.typecheck(env)
        else:
            members_type = langtypes.Struct.Members({})

        mem_len, param_len = len(members_type), len(ty.members)
        if mem_len < param_len:
            raise  # TODO insufficient members
        if mem_len > param_len:
            raise  # TODO too many members
        if members_type != ty.members:
            raise  # TODO type mismatch

        self.type = ty
        return self.type

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
        assert isinstance(self.type, langtypes.Struct)

        return langvalues.StructValue(
            name=self.type.struct_name,
            attrs=self.args.eval(env) if self.args else {},
        )


@dataclass
class Term(Expression):
    left: Expression
    op: Token
    right: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, "+" | "-", langtypes.INT:
                self.type = langtypes.INT
            case langtypes.STRING, "+", langtypes.STRING:
                self.type = langtypes.STRING
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

        return self.type

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
class Factor(Expression):
    left: Expression
    op: Token
    right: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, "*" | "/" | "%", langtypes.INT:
                self.type = langtypes.INT
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

        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        left = self.left.eval(env)
        right = self.right.eval(env)
        match self.op:
            case "*":
                return left * right
            case "/":
                match self.left.type, self.right.type:
                    case langtypes.INT, langtypes.INT:
                        return left // right
                    case _:
                        raise errors.InternalCompilerError(
                            f"{type(self).__name__} recieved invalid operator {self.op}"
                        )
            case "%":
                match self.left.type, self.right.type:
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
class Comparison(Expression):
    left: Expression
    op: Token
    right: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.INT, ">" | "<" | "<=" | ">=", langtypes.INT:
                self.type = langtypes.BOOL
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

        return self.type

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
class Logical(Expression):
    left: Expression
    op: Token
    right: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        match left_type, self.op, right_type:
            case langtypes.BOOL, "&&", langtypes.BOOL:
                self.type = langtypes.BOOL
            case langtypes.BOOL, "||", langtypes.BOOL:
                self.type = langtypes.BOOL
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

        return self.type

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
class Equality(Expression):
    left: Expression
    op: Token
    right: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        left_type = self.left.typecheck(env)
        right_type = self.right.typecheck(env)

        if left_type == right_type and self.op in ("==", "!="):  # pyright: ignore [reportUnnecessaryContains]
            self.type = langtypes.BOOL
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

        return self.type

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
class UnaryOp(Expression):
    op: Token
    operand: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        operand_type = self.operand.typecheck(env)

        match self.op, operand_type:
            case "+" | "-", langtypes.INT:
                self.type = operand_type
            case "!", langtypes.BOOL:
                self.type = operand_type
            case _:
                op_span = errors.Span.from_token(self.op)
                raise errors.InvalidOperationError(
                    message=f"Invalid operation '{self.op}' for type '{operand_type.name}'",
                    span=self.span,
                    operator=errors.OperatorSpan(self.op, op_span),
                    operands=[errors.OperandSpan(operand_type, self.operand.span)],
                )

        return self.type

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
class BoolLiteral(Expression):
    value: bool

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.BOOL
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class IntLiteral(Expression):
    value: int

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.INT
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class StringLiteral(Expression):
    value: str

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.STRING
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        return self.value


@dataclass
class EnumLiteralSimple(Expression):
    enum_type: Token
    variant: Token

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = env.get_type(self.enum_type)
        if self.type is None:
            raise  # TODO
            # raise errors.UndeclaredType()
        return self.type

    @override
    def eval(self, env: RuntimeEnvironment) -> langvalues.EnumValue:
        return langvalues.EnumValue(ty=self.enum_type, variant=self.variant)


@dataclass
class EnumLiteralTuple(Expression):
    enum_type: Token
    variant: Token
    inner: Expression

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = env.get_type(self.enum_type)
        if self.type is None:
            raise  # TODO
            # raise errors.UndeclaredType()
        if not isinstance(self.type, langtypes.Enum):
            raise  # TODO

        inner_type = self.inner.typecheck(env)
        variant_type = self.type.variant_from_str(self.variant)
        if not isinstance(variant_type, langtypes.Enum.Tuple):
            raise  # TODO

        if variant_type.inner != inner_type:
            raise  # TODO

        return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        return langvalues.EnumTupleValue(
            ty=self.enum_type,
            variant=self.variant,
            tuple_value=self.inner.eval(env),
        )


@dataclass
class Variable(Expression):
    value: str

    @override
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = env.get_var_type(self.value)
        if self.type is None:
            raise errors.UnknownVariable(
                message=f"Variable '{self.value}' not declared in this scope",
                span=self.span,
                variable=self.value,
            )
        else:
            return self.type

    @override
    def eval(self, env: RuntimeEnvironment):
        return env.get(self.value)


class WildcardPattern(Ast):
    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.PLACEHOLDER
        return self.type

    def eval(self, env: RuntimeEnvironment):
        pass  # TODO: remove
