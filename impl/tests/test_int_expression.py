from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import Term, IntLiteral, UnaryOp
from compiler.langtypes import Int


def test_addition_with_positive_int():
    ast = parse_tree_to_ast(parse("1+2"))
    assert ast.to_dict() == {
        Term: {
            "left": {IntLiteral: {"value": 1}},
            "op": "+",
            "right": {IntLiteral: {"value": 2}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == 3


def test_addition_with_negative_int_right():
    ast = parse_tree_to_ast(parse("1+-2"))
    assert ast.to_dict() == {
        Term: {
            "left": {IntLiteral: {"value": 1}},
            "op": "+",
            "right": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 2}},
                }
            },
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {IntLiteral: Int},
        "right": {
            UnaryOp: Int,
            "operand": {IntLiteral: Int},
        },
    }
    assert ast.eval() == -1


def test_addition_with_negative_int_left():
    ast = parse_tree_to_ast(parse("-1+2"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 1}},
                }
            },
            "op": "+",
            "right": {IntLiteral: {"value": 2}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {
            UnaryOp: Int,
            "operand": {IntLiteral: Int},
        },
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == 1


def test_addition_with_negative_int_both():
    ast = parse_tree_to_ast(parse("-1+-2"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 1}},
                }
            },
            "op": "+",
            "right": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 2}},
                }
            },
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {
            UnaryOp: Int,
            "operand": {IntLiteral: Int},
        },
        "right": {
            UnaryOp: Int,
            "operand": {IntLiteral: Int},
        },
    }
    assert ast.eval() == -3


def test_subtraction_with_positive_int():
    ast = parse_tree_to_ast(parse("1-2"))
    assert ast.to_dict() == {
        Term: {
            "left": {IntLiteral: {"value": 1}},
            "op": "-",
            "right": {IntLiteral: {"value": 2}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == -1


def test_subtraction_with_negative_int_right():
    ast = parse_tree_to_ast(parse("1--2"))
    assert ast.to_dict() == {
        Term: {
            "left": {IntLiteral: {"value": 1}},
            "op": "-",
            "right": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 2}},
                }
            },
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {IntLiteral: Int},
        "right": {
            UnaryOp: Int,
            "operand": {IntLiteral: Int},
        },
    }
    assert ast.eval() == 3


def test_subtraction_with_negative_int_left():
    ast = parse_tree_to_ast(parse("-1-2"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 1}},
                }
            },
            "op": "-",
            "right": {IntLiteral: {"value": 2}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {
            UnaryOp: Int,
            "operand": {IntLiteral: Int},
        },
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == -3


def test_subtraction_with_negative_int_both():
    ast = parse_tree_to_ast(parse("-1--2"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 1}},
                }
            },
            "op": "-",
            "right": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 2}},
                }
            },
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {
            UnaryOp: Int,
            "operand": {IntLiteral: Int},
        },
        "right": {
            UnaryOp: Int,
            "operand": {IntLiteral: Int},
        },
    }
    assert ast.eval() == 1
