from dataclasses import dataclass
from typing_extensions import override

from compiler import errors, langtypes
from compiler.ast.annotation import TypeAnnotation
from compiler.ast.base import Ast
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
