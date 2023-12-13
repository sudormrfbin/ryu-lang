from .compiler import compile

with open("input.lang", "r") as f:
    inp = f.read()

output = compile(inp)
print(output)
