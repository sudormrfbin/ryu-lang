from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import IntLiteral, StringLiteral, UnaryOp, BoolLiteral
from compiler.langtypes import Int, Bool, String


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


def test_string_literal():
    ast = parse_tree_to_ast(parse('"string"'))
    assert ast.to_dict() == {StringLiteral: {"value": "string"}}
    ast.typecheck()
    assert ast.to_type_dict() == {StringLiteral: String}
    assert ast.eval() == "string"


def test_string_with_spaces_literal():
    ast = parse_tree_to_ast(parse('"string with spaces"'))
    assert ast.to_dict() == {StringLiteral: {"value": "string with spaces"}}
    ast.typecheck()
    assert ast.to_type_dict() == {StringLiteral: String}
    assert ast.eval() == "string with spaces"


def test_empty_string_literal():
    ast = parse_tree_to_ast(parse('""'))
    assert ast.to_dict() == {StringLiteral: {"value": ""}}
    ast.typecheck()
    assert ast.to_type_dict() == {StringLiteral: String}
    assert ast.eval() == ""
