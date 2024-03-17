from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import Assignment, IntLiteral, StatementBlock, VariableDeclaration
from compiler.langtypes import INT, Block, Int
from textwrap import dedent


def test_variable_assignment():
    """
    let x = 1
    x = 4
    """
    source = dedent(test_variable_assignment.__doc__).strip()  # type: ignore
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {
        StatementBlock: {
            "stmts": [
                {
                    VariableDeclaration: {
                        "ident": "x",
                        "rvalue": {IntLiteral: {"value": 1}},
                    },
                },
                {
                    Assignment: {
                        "lvalue": "x",
                        "rvalue": {IntLiteral: {"value": 4}},
                    },
                },
            ],
        },
    }

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == {
        StatementBlock: Block,
        "stmts": [
            {
                VariableDeclaration: Int,
                "rvalue": {IntLiteral: Int},
            },
            {
                Assignment: Int,
                "rvalue": {IntLiteral: Int},
            },
        ],
    }

    assert type_env.get("x") == INT

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 4
