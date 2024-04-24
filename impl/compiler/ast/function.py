from dataclasses import dataclass
from typing import Any, Optional
from typing_extensions import override

from compiler import langtypes, langvalues, runtime
from compiler.ast.annotation import TypeAnnotation
from compiler.ast.base import Ast
from compiler.ast.expressions import Expression
from compiler.ast.statements import Statement, StatementBlock
from compiler.ast.struct import StructInitMembers
from compiler.ast.variable import Variable
from compiler.env import FunctionDefScope, RuntimeEnvironment, TypeEnvironment
from compiler.lalr import Token


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
    def eval(self, env: RuntimeEnvironment) -> Any:
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

    def eval(self, env: RuntimeEnvironment) -> list[Any]:
        return [arg.eval(env) for arg in self.args]


@dataclass
class FunctionCall(Expression):  # TODO: rename to FunctionCallOrStructInit
    callee: Variable
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
    def eval(self, env: RuntimeEnvironment) -> Any:
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
