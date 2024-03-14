from compiler.env import RuntimeEnvironment, TypeEnvironment
from .compiler import run


def repl() -> None:
    type_env = TypeEnvironment()
    runtime_env = RuntimeEnvironment()

    while True:
        try:
            source = input(">> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            break

        if not source:
            continue

        result = run(source, type_env, runtime_env)
        if result is not None:
            print(result)
