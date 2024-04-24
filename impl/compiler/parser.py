from typing import Any, Type, TypeVar

from compiler import ast
from compiler.ast.base import Ast
from compiler.lalr import Meta, Token, Tree, Lark_StandAlone, v_args, Transformer, DATA  # type: ignore

# https://github.com/lark-parser/lark/issues/565
DATA["options"]["maybe_placeholders"] = True  # type: ignore
_parser = Lark_StandAlone(propagate_positions=True)


def parse(source: str) -> Tree[Token]:
    return _parser.parse(source)  # type: ignore


T = TypeVar("T")


def listify(cls: Type[T]):
    @v_args(meta=True, inline=False)  # type: ignore
    def _(self: "LarkTreeToAstTransformer", meta: Meta, lst: list[Any]) -> T:
        return cls(meta, lst)

    return _


@v_args(meta=True, inline=True)  # type: ignore
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
    variable_declaration = ast.variable.VariableDeclaration
    assignment = ast.variable.Assignment
    index_assignment = ast.array.IndexAssignment
    print_stmt = ast.PrintStmt
    if_chain = ast.if_stmt.IfChain
    if_stmt = ast.if_stmt.IfStmt
    else_if_ladder = listify(ast.if_stmt.ElseIfLadder)
    else_if_stmt = ast.if_stmt.ElseIfStmt
    match_stmt = ast.match.MatchStmt
    case_ladder = listify(ast.match.CaseLadder)
    case_stmt = ast.match.CaseStmt
    enum_pattern = ast.match.EnumPattern
    enum_pattern_tuple = ast.match.EnumPatternTuple
    wildcard_pattern = ast.match.WildcardPattern
    while_stmt = ast.WhileStmt
    for_stmt = ast.ForStmt
    for_stmt_int = ast.ForStmtInt
    struct_stmt = ast.struct.StructStmt
    struct_members = listify(ast.struct.StructMembers)
    struct_member = ast.struct.StructMember
    struct_access = ast.struct.StructAccess
    struct_assignment = ast.struct.StructAssignment
    enum_stmt = ast.enum.EnumStmt
    enum_members = listify(ast.enum.EnumMembers)
    enum_member_bare = ast.enum.EnumMemberBare
    enum_member_tuple = ast.enum.EnumMemberTuple
    function_definition = ast.function.FunctionDefinition
    function_params = listify(ast.function.FunctionParams)
    function_param = ast.function.FunctionParam
    type_annotation = ast.TypeAnnotation
    return_stmt = ast.function.ReturnStmt
    equality = ast.Equality
    logical = ast.Logical
    comparison = ast.Comparison
    term = ast.Term
    factor = ast.Factor
    unary_op = ast.UnaryOp
    indexing = ast.array.Indexing
    function_call = ast.function.FunctionCall
    function_args = listify(ast.function.FunctionArgs)
    struct_init_members = listify(ast.struct.StructInitMembers)
    struct_init_member = ast.struct.StructInitMember
    bool_literal = ast.literals.BoolLiteral
    int_literal = ast.literals.IntLiteral
    string_literal = ast.StringLiteral
    enum_literal_simple = ast.EnumLiteralSimple
    enum_literal_tuple = ast.EnumLiteralTuple
    variable = ast.variable.Variable
    array_literal = ast.array.ArrayLiteral
    array_elements = listify(ast.array.ArrayElements)
    array_element = ast.array.ArrayElement
    array_pattern = listify(ast.match.ArrayPattern)
    array_pattern_element = ast.match.ArrayPatternElement


_transformer = LarkTreeToAstTransformer()


def parse_tree_to_ast(tree: Tree[Token]) -> Ast:
    return _transformer.transform(tree)
