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


def test_addition_3_ints():
    ast = parse_tree_to_ast(parse("1+2+6"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                IntLiteral: {"value": 1},
            },
            "op": "+",
            "right": {
                Term: {
                    "left": {
                        IntLiteral: {"value": 2},
                    },
                    "op": "+",
                    "right": {
                        IntLiteral: {"value": 6},
                    },
                },
            },
        },
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {IntLiteral: Int},
        "right": {
            Term: Int,
            "left": {IntLiteral: Int},
            "right": {IntLiteral: Int},
        },
    }
    assert ast.eval() == 9

#For Multiplication
    
def test_multiplication_with_positive_int():
    ast = parse_tree_to_ast(parse("3*2"))
    assert ast.to_dict() == {
        Term: {
            "left": {IntLiteral: {"value": 3}},
            "op": "*",
            "right": {IntLiteral: {"value": 2}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == 6

def test_multiplication_with_negative_int_right():
    ast = parse_tree_to_ast(parse("3*-2"))
    assert ast.to_dict() == {
        Term: {
            "left": {IntLiteral: {"value": 3}},
            "op": "*",
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
    assert ast.eval() == -6

def test_multiplication_with_negative_int_left():
    ast = parse_tree_to_ast(parse("-3*2"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 3}},
                }
            },
            "op": "*",
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
    assert ast.eval() == -6

def test_multiplication_with_negative_int_both():
    ast = parse_tree_to_ast(parse("-3*-2"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 3}},
                }
            },
            "op": "*",
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
    assert ast.eval() == 6

#For Division

def test_division_with_positive_int():
    ast = parse_tree_to_ast(parse("4/2"))
    assert ast.to_dict() == {
        Term: {
            "left": {IntLiteral: {"value": 4}},
            "op": "/",
            "right": {IntLiteral: {"value": 2}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == 2

def test_division_with_negative_int_right():
    ast = parse_tree_to_ast(parse("4/-2"))
    assert ast.to_dict() == {
        Term: {
            "left": {IntLiteral: {"value": 4}},
            "op": "/",
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
    assert ast.eval() == -2

def test_division_with_negative_int_left():
    ast = parse_tree_to_ast(parse("-4/2"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 4}},
                }
            },
            "op": "/",
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
    assert ast.eval() == -2

def test_division_with_negative_int_both():
    ast = parse_tree_to_ast(parse("-4/-2"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 4}},
                }
            },
            "op": "/",
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
    assert ast.eval() == 2

    #test cases for modulus
    
def test_modulus_with_positive_int():
    ast = parse_tree_to_ast(parse("4%2"))
    assert ast.to_dict() == {
        Term: {
            "left": {IntLiteral: {"value": 4}},
            "op": "%",
            "right": {IntLiteral: {"value": 2}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == 0

def test_modulus_with_negative_int_right():
    ast = parse_tree_to_ast(parse("7%-2"))
    assert ast.to_dict() == {
        Term: {
            "left": {IntLiteral: {"value": 7}},
            "op": "%",
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

def test_modulus_with_negative_int_left():
    ast = parse_tree_to_ast(parse("-7%2"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 7}},
                }
            },
            "op": "%",
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

def test_modulus_with_negative_int_both():
    ast = parse_tree_to_ast(parse("-8%-2"))
    assert ast.to_dict() == {
        Term: {
            "left": {
                UnaryOp: {
                    "op": "-",
                    "operand": {IntLiteral: {"value": 8}},
                }
            },
            "op": "%",
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
    assert ast.eval() == 0