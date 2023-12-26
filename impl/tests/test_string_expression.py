from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import Term, StringLiteral
from compiler.langtypes import String


def test_string_concat_2():
    ast = parse_tree_to_ast(parse('"hello"+"world"'))
    assert ast.to_dict() == {
        Term: {
            "left": {StringLiteral: {"value": "hello"}},
            "op": "+",
            "right": {StringLiteral: {"value": "world"}},
        }
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: String,
        "left": {StringLiteral: String},
        "right": {StringLiteral: String},
    }
    assert ast.eval() == "helloworld"


def test_string_concat_3():
    ast = parse_tree_to_ast(parse('"hello"+" "+"world"'))
    assert ast.to_dict() == {
        Term: {
            "left": {
                StringLiteral: {"value": "hello"},
            },
            "op": "+",
            "right": {
                Term: {
                    "left": {
                        StringLiteral: {"value": " "},
                    },
                    "op": "+",
                    "right": {
                        StringLiteral: {"value": "world"},
                    },
                },
            },
        },
    }
    ast.typecheck()
    assert ast.to_type_dict() == {
        Term: String,
        "left": {StringLiteral: String},
        "right": {
            Term: String,
            "left": {StringLiteral: String},
            "right": {StringLiteral: String},
        },
    }
    assert ast.eval() == "hello world"
