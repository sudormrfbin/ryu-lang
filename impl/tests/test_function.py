from compiler.env import TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    FunctionArg,
    FunctionArgs,
    FunctionDefinition,
    IntLiteral,
    StatementBlock,
)
from compiler.langtypes import (
    INT,
    Block,
    Function,
    Int,
    Placeholder,
)
from tests.utils import docstring_source


@docstring_source
def test_function_def(source: str):
    """
    fn sum(a: int, b: int) -> int { 1 }
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        FunctionDefinition: {
            "name": "sum",
            "args": {
                FunctionArgs: {
                    "args": [
                        {FunctionArg: {"name": "a", "arg_type": "int"}},
                        {FunctionArg: {"name": "b", "arg_type": "int"}},
                    ]
                }
            },
            "return_type": "int",
            "body": {StatementBlock: {"stmts": [{IntLiteral: {"value": 1}}]}},
        }
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print(ast.to_type_dict())
    assert ast.to_type_dict() == {
        FunctionDefinition: Function,
        "args": {
            FunctionArgs: Placeholder,
            "args": [{FunctionArg: Int}, {FunctionArg: Int}],
        },
        "body": {StatementBlock: Block, "stmts": [{IntLiteral: Int}]},
    }

    assert type_env.get("sum") == Function(
        function_name="sum", arguments=[INT, INT], return_type=INT
    )
