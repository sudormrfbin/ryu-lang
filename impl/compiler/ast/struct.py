from dataclasses import dataclass
from typing import Any
from typing_extensions import override

from compiler import errors, langtypes
from compiler.ast.annotation import TypeAnnotation
from compiler.ast.base import Ast
from compiler.ast.expressions import Expression
from compiler.ast.statements import Statement
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.lalr import Token


@dataclass
class StructMember(Ast):
    name: Token
    ident_type: TypeAnnotation

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

    def eval(self, env: RuntimeEnvironment) -> Any:
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
    def eval(self, env: RuntimeEnvironment) -> Any:
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
    def eval(self, env: RuntimeEnvironment) -> Any:
        struct_value = env.get(self.struct_access.name)
        value = self.value.eval(env)
        struct_value.set_attr(str(self.struct_access.member), value)
