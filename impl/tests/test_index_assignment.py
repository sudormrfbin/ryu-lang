from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import ArrayElement, ArrayElements, ArrayLiteral, Assignment, IndexAssignment, Indexing, IntLiteral, StatementList, Term, Variable, VariableDeclaration
from compiler.langtypes import INT, Array, Block, Int
from tests.utils import docstring_source


@docstring_source
def test_index_assignment(source: str):
    """
    let x = [2,3]
    x[1]=4
    """
    ast = parse_tree_to_ast(parse(source))
    assert ast.to_dict() =={StatementList: {'stmts': [{VariableDeclaration: {'ident': 'x', 'rvalue': {ArrayLiteral: {'members': {ArrayElements: {'members': [{ArrayElement: {'element': {IntLiteral: {'value': 2}}}}, {ArrayElement: {'element': {IntLiteral: {'value': 3}}}}]}}}}}}, {IndexAssignment: {'arrayname': {Variable: {'value': 'x'}}, 'index': 1, 'value': {IntLiteral: {'value': 4}}}}]}}
    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    print( ast.to_type_dict())
    assert ast.to_type_dict() =={StatementList: Block, 'stmts': [{VariableDeclaration: Array, 'rvalue': {ArrayLiteral: Array, 'members': {ArrayElements: Array, 'members': [{ArrayElement: Int, 'element': {IntLiteral: Int}}, {ArrayElement: Int, 'element': {IntLiteral: Int}}]}}}, {IndexAssignment: Array, 'arrayname': {Variable: Array}, 'value': {IntLiteral:Int}}]}
    assert type_env.get("x") == Array(INT)

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("x") == [2,4]

    
