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

    statement_list = listify(ast.statements.StatementList)
    statement_block = listify(ast.statements.StatementBlock)

    variable_declaration = ast.variable.VariableDeclaration
    variable = ast.variable.Variable
    assignment = ast.variable.Assignment

    array_literal = ast.array.ArrayLiteral
    array_elements = listify(ast.array.ArrayElements)
    array_element = ast.array.ArrayElement
    index_assignment = ast.array.IndexAssignment
    indexing = ast.array.Indexing

    print_stmt = ast.print.PrintStmt

    if_chain = ast.if_stmt.IfChain
    if_stmt = ast.if_stmt.IfStmt
    else_if_ladder = listify(ast.if_stmt.ElseIfLadder)
    else_if_stmt = ast.if_stmt.ElseIfStmt

    match_stmt = ast.match.MatchStmt
    case_ladder = listify(ast.match.CaseLadder)
    case_stmt = ast.match.CaseStmt
    enum_pattern = ast.match.EnumPattern
    enum_pattern_tuple = ast.match.EnumPatternTuple
    array_pattern = listify(ast.match.ArrayPattern)
    array_pattern_element = ast.match.ArrayPatternElement
    wildcard_pattern = ast.match.WildcardPattern

    while_stmt = ast.loops.WhileStmt
    for_stmt = ast.loops.ForStmt
    for_stmt_int = ast.loops.ForStmtInt

    struct_stmt = ast.struct.StructStmt
    struct_members = listify(ast.struct.StructMembers)
    struct_member = ast.struct.StructMember
    struct_access = ast.struct.StructAccess
    struct_assignment = ast.struct.StructAssignment

    struct_init_members = listify(ast.struct.StructInitMembers)
    struct_init_member = ast.struct.StructInitMember

    enum_stmt = ast.enum.EnumStmt
    enum_members = listify(ast.enum.EnumMembers)
    enum_member_bare = ast.enum.EnumMemberBare
    enum_member_tuple = ast.enum.EnumMemberTuple

    enum_literal_simple = ast.enum.EnumLiteralSimple
    enum_literal_tuple = ast.enum.EnumLiteralTuple

    function_definition = ast.function.FunctionDefinition
    function_params = listify(ast.function.FunctionParams)
    function_param = ast.function.FunctionParam
    return_stmt = ast.function.ReturnStmt

    function_call = ast.function.FunctionCall
    function_args = listify(ast.function.FunctionArgs)

    type_annotation = ast.annotation.TypeAnnotation

    equality = ast.operators.Equality
    logical = ast.operators.Logical
    comparison = ast.operators.Comparison
    term = ast.operators.Term
    factor = ast.operators.Factor
    unary_op = ast.operators.UnaryOp

    bool_literal = ast.literals.BoolLiteral
    int_literal = ast.literals.IntLiteral
    string_literal = ast.literals.StringLiteral


_transformer = LarkTreeToAstTransformer()


def parse_tree_to_ast(tree: Tree[Token]) -> Ast:
    return _transformer.transform(tree)
