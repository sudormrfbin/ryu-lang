from typing import Any
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast

EMPTY_ENV = RuntimeEnvironment()
EMPTY_TYPE_ENV = TypeEnvironment()


def test_addition_with_positive_int(snapshot: Any):
    ast = parse_tree_to_ast(parse("1+2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 3


def test_addition_with_negative_int_right(snapshot: Any):
    ast = parse_tree_to_ast(parse("1+-2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == -1


def test_addition_with_negative_int_left(snapshot: Any):
    ast = parse_tree_to_ast(parse("-1+2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 1


def test_addition_with_negative_int_both(snapshot: Any):
    ast = parse_tree_to_ast(parse("-1+-2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == -3


def test_subtraction_with_positive_int(snapshot: Any):
    ast = parse_tree_to_ast(parse("1-2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == -1


def test_subtraction_with_negative_int_right(snapshot: Any):
    ast = parse_tree_to_ast(parse("1--2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 3


def test_subtraction_with_negative_int_left(snapshot: Any):
    ast = parse_tree_to_ast(parse("-1-2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == -3


def test_subtraction_with_negative_int_both(snapshot: Any):
    ast = parse_tree_to_ast(parse("-1--2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 1


def test_addition_3_ints(snapshot: Any):
    ast = parse_tree_to_ast(parse("1+2+6"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 9


# For Multiplication


def test_multiplication_with_positive_int(snapshot: Any):
    ast = parse_tree_to_ast(parse("3*2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 6


def test_multiplication_with_negative_int_right(snapshot: Any):
    ast = parse_tree_to_ast(parse("3*-2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == -6


def test_multiplication_with_negative_int_left(snapshot: Any):
    ast = parse_tree_to_ast(parse("-3*2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == -6


def test_multiplication_with_negative_int_both(snapshot: Any):
    ast = parse_tree_to_ast(parse("-3*-2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 6


# For Division


def test_division_with_positive_int(snapshot: Any):
    ast = parse_tree_to_ast(parse("4/2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 2


def test_division_with_negative_int_right(snapshot: Any):
    ast = parse_tree_to_ast(parse("4/-2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == -2


def test_division_with_negative_int_left(snapshot: Any):
    ast = parse_tree_to_ast(parse("-4/2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == -2


def test_division_with_negative_int_both(snapshot: Any):
    ast = parse_tree_to_ast(parse("-4/-2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 2

    # test cases for modulus


def test_modulus_with_positive_int(snapshot: Any):
    ast = parse_tree_to_ast(parse("4%2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 0


def test_modulus_with_negative_int_right(snapshot: Any):
    ast = parse_tree_to_ast(parse("7%-2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == -1


def test_modulus_with_negative_int_left(snapshot: Any):
    ast = parse_tree_to_ast(parse("-7%2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 1


def test_modulus_with_negative_int_both(snapshot: Any):
    ast = parse_tree_to_ast(parse("-8%-2"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) == 0

    # and and


def test_and_true_and_true(snapshot: Any):
    ast = parse_tree_to_ast(parse("true&&true"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_and_false_and_false(snapshot: Any):
    ast = parse_tree_to_ast(parse("false&&false"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


def test_and_true_and_false(snapshot: Any):
    ast = parse_tree_to_ast(parse("true&&false"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


def test_and_false_and_true(snapshot: Any):
    ast = parse_tree_to_ast(parse("false&&true"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


# for logical OR


def test_and_true_or_true(snapshot: Any):
    ast = parse_tree_to_ast(parse("true||true"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_and_false_or_false(snapshot: Any):
    ast = parse_tree_to_ast(parse("false||false"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


def test_and_true_or_false(snapshot: Any):
    ast = parse_tree_to_ast(parse("true||false"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_and_false_or_true(snapshot: Any):
    ast = parse_tree_to_ast(parse("false||true"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


# For Not Operator


def test_not_true(snapshot: Any):
    ast = parse_tree_to_ast(parse("!true"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


def test_not_false(snapshot: Any):
    ast = parse_tree_to_ast(parse("!false"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


# For Greater Than Operator


def test_greaterthan_largernum_gt_smallernum(snapshot: Any):
    ast = parse_tree_to_ast(parse("5>3"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_greaterthan_smallernum_gt_largernum(snapshot: Any):
    ast = parse_tree_to_ast(parse("3>5"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


# For Lesser Than Operator


def test_lesserthan_largernum_lt_smallernum(snapshot: Any):
    ast = parse_tree_to_ast(parse("5<3"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


def test_lesserthan_smallernum_lt_largernum(snapshot: Any):
    ast = parse_tree_to_ast(parse("3<5"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_ltq_smallernum_ltq_largernum(snapshot: Any):
    ast = parse_tree_to_ast(parse("3<=5"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_ltq_samenum_ltq_samenum(snapshot: Any):
    ast = parse_tree_to_ast(parse("3<=3"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_ltq_largernum_ltq_smallernum(snapshot: Any):
    ast = parse_tree_to_ast(parse("5<=3"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


def test_gtq_smallernum_gtq_largernum(snapshot: Any):
    ast = parse_tree_to_ast(parse("3>=5"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


def test_gtq_samenum_gtq_samenum(snapshot: Any):
    ast = parse_tree_to_ast(parse("3>=3"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_gtq_largernum_gtq_smallernum(snapshot: Any):
    ast = parse_tree_to_ast(parse("5>=3"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_eqeq_samenum(snapshot: Any):
    ast = parse_tree_to_ast(parse("3==3"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True


def test_eqeq_diffnum(snapshot: Any):
    ast = parse_tree_to_ast(parse("3==4"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


def test_noteq_samenum(snapshot: Any):
    ast = parse_tree_to_ast(parse("3!=3"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is False


def test_noteq_diffnum(snapshot: Any):
    ast = parse_tree_to_ast(parse("3!=4"))
    assert ast.to_dict() == snapshot
    ast.typecheck(EMPTY_TYPE_ENV)
    assert ast.to_type_dict() == snapshot
    assert ast.eval(EMPTY_ENV) is True
