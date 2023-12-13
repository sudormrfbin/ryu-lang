from .parser import parse, parse_tree_to_ast


def compile(source: str) -> str:
    tree = parse(source)
    # pprint(tree)
    # print(tree.pretty())
    ast = parse_tree_to_ast(tree)
    # pprint(ast)
    return ast.generate_code()
