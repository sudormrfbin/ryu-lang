from typing import Any

from compiler import ast
from compiler.lalr import Token, Tree, Lark_StandAlone, v_args, Transformer, DATA

# https://github.com/lark-parser/lark/issues/565
DATA["options"]["maybe_placeholders"] = True
_parser = Lark_StandAlone(propagate_positions=True)


def parse(source: str) -> Tree[Token]:
    return _parser.parse(source)


def listify(cls):
    @v_args(meta=True, inline=False)
    def _(self, meta, lst):
        return cls(meta, lst)

    return _


@v_args(meta=True, inline=True)
class LarkTreeToAstTransformer(Transformer[Token, Any]):
    def TRUE(self, _) -> bool:
        return True

    def FALSE(self, _) -> bool:
        return False

    def INT(self, n: str) -> int:
        return int(n)

    def STRING(self, s: str) -> str:
        return s[1:-1]  # remove quotes

    statement_list = listify(ast.StatementList)
    statement_block = listify(ast.StatementBlock)
    variable_declaration = ast.VariableDeclaration
    assignment = ast.Assignment
    index_assignment = ast.IndexAssignment
    print_stmt = ast.PrintStmt
    if_chain = ast.IfChain
    if_stmt = ast.IfStmt
    else_if_ladder = listify(ast.ElseIfLadder)
    else_if_stmt = ast.ElseIfStmt
    match_stmt = ast.MatchStmt
    case_ladder = listify(ast.CaseLadder)
    case_stmt = ast.CaseStmt
    enum_pattern = ast.EnumPattern
    enum_pattern_tuple = ast.EnumPatternTuple
    wildcard_pattern = ast.WildcardPattern
    while_stmt = ast.WhileStmt
    for_stmt = ast.ForStmt
    for_stmt_int = ast.ForStmtInt
    struct_stmt = ast.StructStmt
    struct_members = listify(ast.StructMembers)
    struct_member = ast.StructMember
    struct_access = ast.StructAccess
    struct_assignment = ast.StructAssignment
    enum_stmt = ast.EnumStmt
    enum_members = listify(ast.EnumMembers)
    enum_member_bare = ast.EnumMemberBare
    enum_member_tuple = ast.EnumMemberTuple
    function_definition = ast.FunctionDefinition
    function_params = listify(ast.FunctionParams)
    function_param = ast.FunctionParam
    type_annotation = ast.TypeAnnotation
    return_stmt = ast.ReturnStmt
    equality = ast.Equality
    logical = ast.Logical
    comparison = ast.Comparison
    term = ast.Term
    factor = ast.Factor
    unary_op = ast.UnaryOp
    indexing = ast.Indexing
    function_call = ast.FunctionCall
    function_args = listify(ast.FunctionArgs)
    struct_init_members = listify(ast.StructInitMembers)
    struct_init_member = ast.StructInitMember
    bool_literal = ast.BoolLiteral
    int_literal = ast.IntLiteral
    string_literal = ast.StringLiteral
    enum_literal_simple = ast.EnumLiteralSimple
    enum_literal_tuple = ast.EnumLiteralTuple
    variable = ast.Variable
    array_literal = ast.ArrayLiteral
    array_elements = listify(ast.ArrayElements)
    array_element = ast.ArrayElement
    array_pattern = listify(ast.ArrayPattern)
    array_pattern_element = ast.ArrayPatternElement


_transformer = LarkTreeToAstTransformer()


def parse_tree_to_ast(tree: Tree[Token]) -> ast.Ast:
    return _transformer.transform(tree)
