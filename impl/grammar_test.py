from lark import Lark

grammar = """
%import common.INT

start: if_chain

# if_chain: if_stmt [("else" if_stmt)+] ["else" "{" INT "}"]
if_chain: if_stmt [else_if_ladder] [else_block]
if_stmt: "if" INT "{" INT "}"
else_if_ladder: ("elif" INT "{" INT "}")+
?else_block: "else" "{" INT "}"

%ignore " "
%ignore "\\n"
"""

parser = Lark(
    grammar,
    parser="lalr",
    propagate_positions=True,
)

text = """
if 3 {
    3
} elif 3 {
    3
} else {
    5
}
"""

parser.parse(text)
