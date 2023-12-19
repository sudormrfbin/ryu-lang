# Adapted from https://gist.github.com/roberthoenig/30f08b64b6ba6186a2cdee19502040b4
from typing import Union


# Parse input string into a list of all parentheses and atoms (int or str),
# exclude whitespaces.
def _tokenize(string: str) -> list[str]:
    assert string[0] == "(", f"Expected (, got {string[0]}"

    tokens = ["("]
    last_c = "("

    in_str = False
    buffer = ""

    for c in string[1:]:
        if c == '"' and not in_str:
            in_str = True
        elif c == '"' and in_str:
            in_str = False
            tokens.append(buffer)
            buffer = ""
        elif in_str:
            buffer += c
        elif c.isalnum() or c == "-":
            if last_c.isalnum() or last_c == "-":
                tokens[-1] += c
            else:
                tokens.append(c)
        elif not c.isspace():
            tokens.append(c)
        last_c = c
    return tokens


LispAst = list[Union[str, "LispAst"]]


# Generate abstract syntax tree from normalized input.
def _get_ast(input_norm: list[str]) -> LispAst:
    ast: LispAst = []
    # Go through each element in the input:
    # - if it is an open parenthesis, find matching parenthesis and make recursive
    #   call for content in-between. Add the result as an element to the current list.
    # - if it is an atom, just add it to the current list.
    i = 0
    while i < len(input_norm):
        symbol = input_norm[i]
        if symbol == "(":
            list_content: list[str] = []
            match_ctr = 1  # If 0, parenthesis has been matched.
            while match_ctr != 0:
                i += 1
                if i >= len(input_norm):
                    raise ValueError("Invalid input: Unmatched open parenthesis.")
                symbol = input_norm[i]
                if symbol == "(":
                    match_ctr += 1
                elif symbol == ")":
                    match_ctr -= 1
                if match_ctr != 0:
                    list_content.append(symbol)
            ast.append(_get_ast(list_content))
        elif symbol == ")":
            raise ValueError("Invalid input: Unmatched close parenthesis.")
        else:
            ast.append(symbol)
        i += 1
    return ast


def parse_sexp(input_str: str) -> LispAst:
    normalized = _tokenize(input_str)

    # Due to the recursive nature of the parser, the root node will always be
    # wrapped in a list, so unwrap the list before returning the ast.
    ast = _get_ast(normalized)[0]
    assert isinstance(ast, list)
    return ast


if __name__ == "__main__":
    import sys

    input_str = sys.stdin.read()
    input_norm = _tokenize(input_str)
    ast = _get_ast(input_norm)[0]
    print(ast)
