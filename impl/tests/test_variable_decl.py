from compiler.env import RuntimeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import Equality, Factor, IntLiteral, VariableDeclaration
from compiler.langtypes import Bool, Int


def test_variable_delcaration():
    ast = parse_tree_to_ast(parse("let x = 1"))
    assert ast.to_dict() == {
        VariableDeclaration: {
            "ident": "x",
            "rvalue": {IntLiteral: {"value": 1}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        VariableDeclaration: Int,
        "rvalue": {IntLiteral: Int},
    }

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == 1


def test_variable_delcaration_with_expressions():
    ast = parse_tree_to_ast(parse("let variable = 3 * 4 == 10"))
    assert ast.to_dict() == {
        VariableDeclaration: {
            "ident": "variable",
            "rvalue": {
                Equality: {
                    "left": {
                        Factor: {
                            "left": {IntLiteral: {"value": 3}},
                            "op": "*",
                            "right": {IntLiteral: {"value": 4}},
                        },
                    },
                    "op": "==",
                    "right": {IntLiteral: {"value": 10}},
                },
            },
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        VariableDeclaration: Bool,
        "rvalue": {
            Equality: Bool,
            "left": {
                Factor: Int,
                "left": {IntLiteral: Int},
                "right": {IntLiteral: Int},
            },
            "right": {IntLiteral: Int},
        },
    }

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("variable") == False
