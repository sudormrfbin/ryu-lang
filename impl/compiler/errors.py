from typing import Iterable
from dataclasses import dataclass

from lark.tree import Meta


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
            try:
                to_sexp = getattr(value, "to_sexp")
                sexp.append(to_sexp())
            except AttributeError:
                sexp.append(str(value))

        return sexp


class InvalidOperationError(CompilerError):
    _SEXP_INCLUDE = ("message", "span")

    def __init__(self, message: str, span: Span):
        super().__init__(message, span)

        self.message = message
        self.span = span
