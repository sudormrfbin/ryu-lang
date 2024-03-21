from compiler.env import RuntimeEnvironment, TypeEnvironment
from compiler.parser import parse, parse_tree_to_ast
from compiler.ast import ArrayElement, ArrayElements, ArrayLiteral, Assignment, Indexing, IntLiteral, StatementList, Term, Variable, VariableDeclaration
from compiler.langtypes import INT, Array, Block, Int
from tests.utils import docstring_source


@docstring_source
def test_indexing(source: str):
    """
    let x = [2,3]
    let b=x[1]
    """
    ast = parse_tree_to_ast(parse(source))
 
    assert ast.to_dict() =={StatementList: {'stmts': [{VariableDeclaration: {'ident':  'x', 'rvalue': {ArrayLiteral: {'members': {ArrayElements: {'members': [{ArrayElement: {'element': {IntLiteral: {'value': 2}}}}, {ArrayElement: {'element': {IntLiteral: {'value': 3}}}}]}}}}}}, {VariableDeclaration: {'ident':  'b', 'rvalue': {Indexing: {'element': {Variable: {'value':  'x'}}, 'index': 1}}}}]}}
    type_env = TypeEnvironment()
    ast.typecheck(type_env)
    assert ast.to_type_dict() =={StatementList: Block, 'stmts': [{VariableDeclaration: Array, 'rvalue': {ArrayLiteral: Array, 'members': {ArrayElements: Array, 'members': [{ArrayElement: Int, 'element': {IntLiteral: Int}}, {ArrayElement: Int, 'element': {IntLiteral: Int}}]}}}, {VariableDeclaration: Array, 'rvalue': {Indexing: Array, 'element': {Variable: Array}}}]}
    assert type_env.get("x") == Array(INT)

    env = RuntimeEnvironment()
    ast.eval(env)
    assert env.get("b") == 3
