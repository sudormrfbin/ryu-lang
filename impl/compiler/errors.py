from typing import Iterable
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


class CompilerError(Exception):
    _SEXP_INCLUDE: Iterable[str]

    def to_sexp(self):
        error_name = type(self).__name__
        sexp = [error_name]

        for arg in self._SEXP_INCLUDE:
            sexp.append(":")
            sexp.append(arg)

            value = getattr(self, arg)

            if hasattr(value, attr := "to_sexp"):
                to_sexp = getattr(value, attr)
            elif hasattr(self, attr := f"to_sexp_{arg}"):
                to_sexp = getattr(self, attr)
            else:

                def to_sexp():
                    return str(value)

            sexp.append(to_sexp())

        return sexp


class InvalidOperationError(CompilerError):
    _SEXP_INCLUDE = ("message", "operator", "operands")

    def __init__(
        self,
        message: str,
        operator: tuple[str, Span],
        operands: list[tuple[langtypes.Type, Span]],
    ):
        super().__init__(message, operator, operands)

        self.message = message
        self.operator = operator
        self.operands = operands

    def to_sexp_operator(self):
        return [self.operator[0], self.operator[1].to_sexp()]

    def to_sexp_operands(self):
        sexp = []
        for type_, span in self.operands:
            sexp.append([type_.to_sexp(), span.to_sexp()])

        return sexp
