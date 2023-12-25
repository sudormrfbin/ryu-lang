from .compiler import run


def repl() -> None:
    while True:
        try:
            source = input(">> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            break

        if not source:
            continue

        result = run(source)
        if result is not None:
            print(result)
