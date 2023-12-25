from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import IntLiteral, UnaryOp, BoolLiteral
from compiler.langtypes import Int, Bool


def test_true_literal():
    ast = parse_tree_to_ast(parse("true"))

    assert ast.to_dict() == {
        BoolLiteral: {"value": True},
    }

    ast.typecheck()
    assert ast.to_type_dict() == {BoolLiteral: Bool}

    assert ast.eval() is True


def test_false_literal():
    ast = parse_tree_to_ast(parse("false"))

    assert ast.to_dict() == {
        BoolLiteral: {"value": False},
    }

    ast.typecheck()
    assert ast.to_type_dict() == {BoolLiteral: Bool}

    assert ast.eval() is False


def test_int_literal():
    ast = parse_tree_to_ast(parse("123"))

    assert ast.to_dict() == {
        IntLiteral: {"value": 123},
    }

    ast.typecheck()
    assert ast.to_type_dict() == {IntLiteral: Int}

    assert ast.eval() == 123


def test_negative_signed_int_literal():
    ast = parse_tree_to_ast(parse("-1"))

    assert ast.to_dict() == {
        UnaryOp: {
            "op": "-",
            "operand": {IntLiteral: {"value": 1}},
        }
    }

    ast.typecheck()
    assert ast.to_type_dict() == {
        UnaryOp: Int,
        "operand": {IntLiteral: Int},
    }

    assert ast.eval() == -1


def test_positive_signed_int_literal():
    ast = parse_tree_to_ast(parse("+1"))

    assert ast.to_dict() == {
        UnaryOp: {
            "op": "+",
            "operand": {IntLiteral: {"value": 1}},
        }
    }

    ast.typecheck()
    assert ast.to_type_dict() == {
        UnaryOp: Int,
        "operand": {IntLiteral: Int},
    }

    assert ast.eval() == 1
