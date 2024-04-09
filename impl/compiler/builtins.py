from array import array
from ctypes import Array
import ctypes
from types import BuiltinFunctionType
from typing import TYPE_CHECKING, Any
from typing_extensions import override
from compiler import langtypes
from compiler.langvalues import BuiltinFunction


if TYPE_CHECKING:
    from compiler.env import RuntimeEnvironment


class SumFunction(BuiltinFunction):
    TYPE = langtypes.Function(
        function_name="sum",
        arguments=langtypes.Params([langtypes.INT, langtypes.INT]),
        return_type=langtypes.INT,
    )

    @override
    def call(self, args: list[Any], env: "RuntimeEnvironment") -> Any:
        a: int = args[0]
        b: int = args[1]

        return a + b

class LengthFunction(BuiltinFunction):
    TYPE = langtypes.Function(
        function_name="len",
        arguments=langtypes.Params([langtypes.Array(ty=langtypes.INT)]),
        return_type=langtypes.INT
    )

    @override
    def call(self, args: list[Any], env: "RuntimeEnvironment") -> Any:
        a: list[int] = args[0] 
        
        return len(a)
        
