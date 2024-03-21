from lark import Token
from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import Assignment, IntLiteral, PrintStmt, StatementList, Term, Variable, VariableDeclaration,StringLiteral
from compiler.langtypes import INT, Block, Int, String
from tests.utils import docstring_source


@docstring_source
def test_print(source: str):
    """
    print "hello world"
    """
    ast = parse_tree_to_ast(parse(source))
    print(ast.to_dict())
    assert ast.to_dict() == {PrintStmt: {'expr': {StringLiteral: {'value': 'hello world'}}}}

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() == {PrintStmt: String, 'expr': {StringLiteral:  String}}   

    env = RuntimeEnvironment()
    ast.eval(env)

#test2
@docstring_source
def test_print_variable(source: str):
    """
    let x=2
    print x+1
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() == {StatementList: {'stmts': [{VariableDeclaration: {'ident': Token('IDENTIFIER', 'x'), 'rvalue': {IntLiteral: {'value': 2}}}}, {PrintStmt: {'expr': {Term: {'left': {Variable: {'value': Token('IDENTIFIER', 'x')}}, 'op': Token('PLUS', '+'), 'right': {IntLiteral: {'value': 1}}}}}}]}}

    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print("\n",ast.to_type_dict())
    assert ast.to_type_dict() == {StatementList:Block, 'stmts': [{VariableDeclaration:Int, 'rvalue': {IntLiteral:Int}}, {PrintStmt:Int, 'expr': {Term:Int, 'left': {Variable:Int}, 'right': {IntLiteral:Int}}}]}
    env = RuntimeEnvironment()
    ast.eval(env)
