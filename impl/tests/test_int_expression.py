from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import Term, IntLiteral, UnaryOp, BoolLiteral, Factor, Comparison, Logical, Equality
from compiler.langtypes import Int, Bool


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


# For Multiplication


def test_multiplication_with_positive_int():
    ast = parse_tree_to_ast(parse("3*2"))
    assert ast.to_dict() == {
        Factor: {
            "left": {IntLiteral: {"value": 3}},
            "op": "*",
            "right": {IntLiteral: {"value": 2}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Factor: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == 6


def test_multiplication_with_negative_int_right():
    ast = parse_tree_to_ast(parse("3*-2"))
    assert ast.to_dict() == {
        Factor: {
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
        Factor: Int,
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
        Factor: {
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
        Factor: Int,
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
        Factor: {
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
        Factor: Int,
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


# For Division


def test_division_with_positive_int():
    ast = parse_tree_to_ast(parse("4/2"))
    assert ast.to_dict() == {
        Factor: {
            "left": {IntLiteral: {"value": 4}},
            "op": "/",
            "right": {IntLiteral: {"value": 2}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Factor: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == 2


def test_division_with_negative_int_right():
    ast = parse_tree_to_ast(parse("4/-2"))
    assert ast.to_dict() == {
        Factor: {
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
        Factor: Int,
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
        Factor: {
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
        Factor: Int,
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
        Factor: {
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
        Factor: Int,
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

    # test cases for modulus


def test_modulus_with_positive_int():
    ast = parse_tree_to_ast(parse("4%2"))
    assert ast.to_dict() == {
        Factor: {
            "left": {IntLiteral: {"value": 4}},
            "op": "%",
            "right": {IntLiteral: {"value": 2}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Factor: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == 0


def test_modulus_with_negative_int_right():
    ast = parse_tree_to_ast(parse("7%-2"))
    assert ast.to_dict() == {
        Factor: {
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
        Factor: Int,
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
        Factor: {
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
        Factor: Int,
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
        Factor: {
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
        Factor: Int,
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

    # and and


def test_and_true_and_true():
    ast = parse_tree_to_ast(parse("true&&true"))
    assert ast.to_dict() == {
        Logical: {
            "left": {BoolLiteral: {"value": True}},
            "op": "&&",
            "right": {BoolLiteral: {"value": True}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Logical: Bool,
        "left": {BoolLiteral: Bool},
        "right": {BoolLiteral: Bool},
    }
    assert ast.eval() == True


def test_and_false_and_false():
    ast = parse_tree_to_ast(parse("false&&false"))
    assert ast.to_dict() == {
        Logical: {
            "left": {BoolLiteral: {"value": False}},
            "op": "&&",
            "right": {BoolLiteral: {"value": False}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Logical: Bool,
        "left": {BoolLiteral: Bool},
        "right": {BoolLiteral: Bool},
    }
    assert ast.eval() == False


def test_and_true_and_false():
    ast = parse_tree_to_ast(parse("true&&false"))
    assert ast.to_dict() == {
        Logical: {
            "left": {BoolLiteral: {"value": True}},
            "op": "&&",
            "right": {BoolLiteral: {"value": False}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Logical: Bool,
        "left": {BoolLiteral: Bool},
        "right": {BoolLiteral: Bool},
    }
    assert ast.eval() == False


def test_and_false_and_true():
    ast = parse_tree_to_ast(parse("false&&true"))
    assert ast.to_dict() == {
        Logical: {
            "left": {BoolLiteral: {"value": False}},
            "op": "&&",
            "right": {BoolLiteral: {"value": True}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Logical: Bool,
        "left": {BoolLiteral: Bool},
        "right": {BoolLiteral: Bool},
    }
    assert ast.eval() == False


# for logical OR


def test_and_true_or_true():
    ast = parse_tree_to_ast(parse("true||true"))
    assert ast.to_dict() == {
        Logical: {
            "left": {BoolLiteral: {"value": True}},
            "op": "||",
            "right": {BoolLiteral: {"value": True}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Logical: Bool,
        "left": {BoolLiteral: Bool},
        "right": {BoolLiteral: Bool},
    }
    assert ast.eval() == True


def test_and_false_or_false():
    ast = parse_tree_to_ast(parse("false||false"))
    assert ast.to_dict() == {
        Logical: {
            "left": {BoolLiteral: {"value": False}},
            "op": "||",
            "right": {BoolLiteral: {"value": False}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Logical: Bool,
        "left": {BoolLiteral: Bool},
        "right": {BoolLiteral: Bool},
    }
    assert ast.eval() == False


def test_and_true_or_false():
    ast = parse_tree_to_ast(parse("true||false"))
    assert ast.to_dict() == {
        Logical: {
            "left": {BoolLiteral: {"value": True}},
            "op": "||",
            "right": {BoolLiteral: {"value": False}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Logical: Bool,
        "left": {BoolLiteral: Bool},
        "right": {BoolLiteral: Bool},
    }
    assert ast.eval() == True


def test_and_false_or_true():
    ast = parse_tree_to_ast(parse("false||true"))
    assert ast.to_dict() == {
        Logical: {
            "left": {BoolLiteral: {"value": False}},
            "op": "||",
            "right": {BoolLiteral: {"value": True}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Logical: Bool,
        "left": {BoolLiteral: Bool},
        "right": {BoolLiteral: Bool},
    }
    assert ast.eval() == True


# For Not Operator


def test_not_true():
    ast = parse_tree_to_ast(parse("!true"))
    assert ast.to_dict() == {
        UnaryOp: {
            "op": "!",
            "operand": {BoolLiteral: {"value": True}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        UnaryOp: Bool,
        "operand": {BoolLiteral: Bool},
    }
    assert ast.eval() == False


def test_not_false():
    ast = parse_tree_to_ast(parse("!false"))
    assert ast.to_dict() == {
        UnaryOp: {
            "op": "!",
            "operand": {BoolLiteral: {"value": False}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        UnaryOp: Bool,
        "operand": {BoolLiteral: Bool},
    }
    assert ast.eval() == True


# For Greater Than Operator


def test_greaterthan_largernum_gt_smallernum():
    ast = parse_tree_to_ast(parse("5>3"))
    assert ast.to_dict() == {
        Comparison: {
            "left": {IntLiteral: {"value": 5}},
            "op": ">",
            "right": {IntLiteral: {"value": 3}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Comparison: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == True


def test_greaterthan_smallernum_gt_largernum():
    ast = parse_tree_to_ast(parse("3>5"))
    assert ast.to_dict() == {
        Comparison: {
            "left": {IntLiteral: {"value": 3}},
            "op": ">",
            "right": {IntLiteral: {"value": 5}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Comparison: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == False


# For Lesser Than Operator


def test_lesserthan_largernum_lt_smallernum():
    ast = parse_tree_to_ast(parse("5<3"))
    assert ast.to_dict() == {
        Comparison: {
            "left": {IntLiteral: {"value": 5}},
            "op": "<",
            "right": {IntLiteral: {"value": 3}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Comparison: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == False


def test_lesserthan_smallernum_lt_largernum():
    ast = parse_tree_to_ast(parse("3<5"))
    assert ast.to_dict() == {
        Comparison: {
            "left": {IntLiteral: {"value": 3}},
            "op": "<",
            "right": {IntLiteral: {"value": 5}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Comparison: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == True


def test_ltq_smallernum_ltq_largernum():
    ast = parse_tree_to_ast(parse("3<=5"))
    assert ast.to_dict() == {
        Comparison: {
            "left": {IntLiteral: {"value": 3}},
            "op": "<=",
            "right": {IntLiteral: {"value": 5}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Comparison: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == True


def test_ltq_samenum_ltq_samenum():
    ast = parse_tree_to_ast(parse("3<=3"))
    assert ast.to_dict() == {
        Comparison: {
            "left": {IntLiteral: {"value": 3}},
            "op": "<=",
            "right": {IntLiteral: {"value": 3}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Comparison: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == True


def test_ltq_largernum_ltq_smallernum():
    ast = parse_tree_to_ast(parse("5<=3"))
    assert ast.to_dict() == {
        Comparison: {
            "left": {IntLiteral: {"value": 5}},
            "op": "<=",
            "right": {IntLiteral: {"value": 3}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Comparison: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == False


def test_gtq_smallernum_gtq_largernum():
    ast = parse_tree_to_ast(parse("3>=5"))
    assert ast.to_dict() == {
        Comparison: {
            "left": {IntLiteral: {"value": 3}},
            "op": ">=",
            "right": {IntLiteral: {"value": 5}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Comparison: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == False


def test_gtq_samenum_gtq_samenum():
    ast = parse_tree_to_ast(parse("3>=3"))
    assert ast.to_dict() == {
        Comparison: {
            "left": {IntLiteral: {"value": 3}},
            "op": ">=",
            "right": {IntLiteral: {"value": 3}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Comparison: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == True


def test_gtq_largernum_gtq_smallernum():
    ast = parse_tree_to_ast(parse("5>=3"))
    assert ast.to_dict() == {
        Comparison: {
            "left": {IntLiteral: {"value": 5}},
            "op": ">=",
            "right": {IntLiteral: {"value": 3}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Comparison: Int,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == True

def test_eqeq_samenum():
    ast = parse_tree_to_ast(parse("3==3"))
    assert ast.to_dict() == {
        Equality: {
            "left": {IntLiteral: {"value": 3}},
            "op": "==",
            "right": {IntLiteral: {"value": 3}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Equality: Bool,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == True

def test_eqeq_diffnum():
    ast = parse_tree_to_ast(parse("3==4"))
    assert ast.to_dict() == {
        Equality: {
            "left": {IntLiteral: {"value": 3}},
            "op": "==",
            "right": {IntLiteral: {"value": 4}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Equality: Bool,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == False

def test_noteq_samenum():
    ast = parse_tree_to_ast(parse("3!=3"))
    assert ast.to_dict() == {
        Equality: {
            "left": {IntLiteral: {"value": 3}},
            "op": "!=",
            "right": {IntLiteral: {"value": 3}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Equality: Bool,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == False

def test_noteq_diffnum():
    ast = parse_tree_to_ast(parse("3!=4"))
    assert ast.to_dict() == {
        Equality: {
            "left": {IntLiteral: {"value": 3}},
            "op": "!=",
            "right": {IntLiteral: {"value": 4}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Equality: Bool,
        "left": {IntLiteral: Int},
        "right": {IntLiteral: Int},
    }
    assert ast.eval() == True