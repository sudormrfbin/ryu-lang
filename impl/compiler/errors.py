import dataclasses
from dataclasses import dataclass

from lark.tree import Meta

from compiler import langtypes


@dataclass
class Span:
    start_line: int
    end_line: int
    start_column: int
    end_column: int

    @classmethod
    def from_meta(cls, meta: Meta) -> "Span":
        return cls(
            start_line=meta.line,
            end_line=meta.end_line,
            start_column=meta.column,
            end_column=meta.end_column,
        )

    def to_sexp(self):
        start = f"{self.start_line}:{self.start_column}"
        end = f"{self.end_line}:{self.end_column}"

        return ["Span", ":", "start", start, ":", "end", end]


@dataclass
class CompilerError(Exception):
    def __post_init__(self):
        attributes = dataclasses.astuple(self)
        # Custom exceptions must always call super(), we use the __post_init__
        # mechanism provided by dataclasses to call the super constructor after
        # this class's __init__ is called.
        super().__init__(*attributes)

    def to_sexp(self):
        error_name = type(self).__name__
        sexp = [error_name]

        for field, value in dataclasses.asdict(self).items():
            sexp.append(":")
            sexp.append(field)

            if hasattr(value, fn := "to_sexp"):
                to_sexp = getattr(value, fn)
            elif hasattr(self, fn := f"to_sexp_{field}"):
                to_sexp = getattr(self, fn)
            else:

                def to_sexp():
                    return str(value)

            sexp.append(to_sexp())

        return sexp


@dataclass
class InvalidOperationError(CompilerError):
    message: str
    operator: tuple[str, Span]
    operands: list[tuple[langtypes.Type, Span]]

    def to_sexp_operator(self):
        return [self.operator[0], self.operator[1].to_sexp()]

    def to_sexp_operands(self):
        sexp = []
        for type_, span in self.operands:
            sexp.append([type_.to_sexp(), span.to_sexp()])

        return sexp
