from typing import TYPE_CHECKING, Any
from typing_extensions import override
from compiler import langtypes
from compiler.langvalues import BuiltinFunction


if TYPE_CHECKING:
    from compiler.env import RuntimeEnvironment


class SumFunction(BuiltinFunction):
    TYPE = langtypes.Function(
        function_name="sum",
        arguments=langtypes.Function.Params([langtypes.INT, langtypes.INT]),
        return_type=langtypes.INT,
    )

    @override
    def call(self, args: list[Any], env: "RuntimeEnvironment") -> Any:
        a: int = args[0]
        b: int = args[1]

        return a + b


class ArrayLengthFunction(BuiltinFunction):
    TYPE = langtypes.Function(
        function_name="arrlen",
        arguments=langtypes.Function.Params([langtypes.Array(ty=langtypes.INT)]),
        return_type=langtypes.INT,
    )

    @override
    def call(self, args: list[Any], env: "RuntimeEnvironment") -> Any:
        a: list[int] = args[0]

        return len(a)


class StringLengthFunction(BuiltinFunction):
    TYPE = langtypes.Function(
        function_name="strlen",
        arguments=langtypes.Function.Params([langtypes.STRING]),
        return_type=langtypes.INT,
    )

    @override
    def call(self, args: list[Any], env: "RuntimeEnvironment") -> Any:
        a: str = args[0]

        return len(a)


class ArrayAppend(BuiltinFunction):
    TYPE = langtypes.Function(
        function_name="append",
        arguments=langtypes.Function.Params(
            [langtypes.Array(langtypes.INT), langtypes.INT]
        ),
        return_type=langtypes.Array(langtypes.INT),
    )

    @override
    def call(self, args: list[Any], env: "RuntimeEnvironment") -> Any:
        a: list[int] = args[0]
        b: int = args[1]

        return a.append(b)
