from dataclasses import dataclass
from typing import Any, Optional
from typing_extensions import override

from compiler import errors, langtypes
from compiler.ast.base import Ast
from compiler.ast.annotation import TypeAnnotation
from compiler.ast.expressions import Expression
from compiler.ast.statements import Statement
from compiler.ast.variable import Variable
from compiler.env import RuntimeEnvironment, TypeEnvironment


@dataclass
class ArrayElement(Ast):
    element: Expression

    def typecheck(self, env: TypeEnvironment) -> langtypes.Type:
        self.type = self.element.typecheck(env)
        return self.type

    def eval(self, env: RuntimeEnvironment) -> Any:
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

    def eval(self, env: RuntimeEnvironment) -> Any:
        result: list[Any] = []
        for mem in self.members:
            result.append(mem.eval(env))
        return result


@dataclass
class ArrayLiteral(Ast):
    declared_type: Optional[TypeAnnotation]
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

    def eval(self, env: RuntimeEnvironment) -> Any:
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

    def eval(self, env: RuntimeEnvironment) -> Any:
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
    arrayname: Variable
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
    def eval(self, env: RuntimeEnvironment):
        array_name = self.arrayname.eval(env)
        array_value = self.value.eval(env)
        array_index = self.index.eval(env)
        array_name[array_index] = array_value
