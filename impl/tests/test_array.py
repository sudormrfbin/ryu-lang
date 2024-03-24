from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import (
    ArrayElement,
    ArrayElements,
    ArrayLiteral,
    Assignment,
    IntLiteral,
    StatementList,
    Term,
    VariableDeclaration,
)
from compiler.langtypes import INT, Array, Block, Int
from tests.utils import docstring_source


@docstring_source
def test_array_statement_basic(source: str):
    """
    let x = [2,3+3]
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        VariableDeclaration: {
            "ident": "x",
            "rvalue": {
                ArrayLiteral: {
                    "members": {
                        ArrayElements: {
                            "members": [
                                {ArrayElement: {"element": {IntLiteral: {"value": 2}}}},
                                {
                                    ArrayElement: {
                                        "element": {
                                            Term: {
                                                "left": {IntLiteral: {"value": 3}},
                                                "op": "+",
                                                "right": {IntLiteral: {"value": 3}},
                                            }
                                        }
                                    }
                                },
                            ]
                        }
                    }
                }
            },
        }
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == {
        VariableDeclaration: Array,
        "rvalue": {
            ArrayLiteral: Array,
            "members": {
                ArrayElements: Array,
                "members": [
                    {ArrayElement: Int, "element": {IntLiteral: Int}},
                    {
                        ArrayElement: Int,
                        "element": {
                            Term: Int,
                            "left": {IntLiteral: Int},
                            "right": {IntLiteral: Int},
                        },
                    },
                ],
            },
        },
    }

    assert type_env.get("x") == Array(INT)

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == [2, 6]
