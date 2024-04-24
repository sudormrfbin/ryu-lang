from dataclasses import dataclass
from typing_extensions import override

from compiler import errors, langtypes, langvalues
from compiler.ast.annotation import TypeAnnotation
from compiler.ast.base import Ast
from compiler.ast.expressions import Expression
from compiler.ast.statements import Statement
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.lalr import Token


@dataclass
class EnumMemberBare(Ast):
    name: Token

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = langtypes.Type()  # TODO: assign separate type
        return self.type


@dataclass
class EnumMemberTuple(Ast):
    name: Token
    tuple_members: TypeAnnotation

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


# =============================== Literals ================================


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
