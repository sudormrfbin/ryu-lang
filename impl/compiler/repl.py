from compiler.env import RuntimeEnvironment, TypeEnvironment
from .compiler import run


def repl() -> None:
    type_env = TypeEnvironment()
    runtime_env = RuntimeEnvironment()

    while True:
        try:
            source = read_statement()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            break

        if not source:
            continue

        result = run(source, type_env, runtime_env)
        if result is not None:
            print(result)

def read_statement():
    source = input(">> ").strip()

    while not scope_is_balanced(source):
        source += input(".. ").strip()

    return source

def scope_is_balanced(string: str) -> bool:
    stack = []

    for char in string:
        if char == '{':
            stack.append(char)
        elif char == '}':
            if not stack:
                return False  # Found a closing brace without a corresponding opening brace
            stack.pop()
    
    return not stack  # If stack is empty, braces are balanced
