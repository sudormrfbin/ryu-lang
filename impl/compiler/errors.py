from typing import ClassVar
import dataclasses
from dataclasses import dataclass

from lark.tree import Meta
from lark.lexer import Token

from compiler import langtypes


@dataclass
class Span:
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    start_pos: int
    end_pos: int

    @classmethod
    def from_meta(cls, meta: Meta) -> "Span":
        return cls(
            start_line=meta.line,
            end_line=meta.end_line,
            start_column=meta.column,
            end_column=meta.end_column,
            start_pos=meta.start_pos,
            end_pos=meta.end_pos,
        )

    @classmethod
    def from_token(cls, token: Token) -> "Span":
        assert token.line
        assert token.end_line
        assert token.column
        assert token.end_column
        assert token.start_pos
        assert token.end_pos

        return cls(
            start_line=token.line,
            end_line=token.end_line,
            start_column=token.column,
            end_column=token.end_column,
            start_pos=token.start_pos,
            end_pos=token.end_pos,
        )

    def to_sexp(self):
        start = f"{self.start_line}:{self.start_column}"
        end = f"{self.end_line}:{self.end_column}"

        return ["Span", ":", "start", start, ":", "end", end]


class InternalCompilerError(Exception):
    pass


@dataclass
class CompilerError(Exception):
    code: ClassVar[int]

    message: str
    span: Span

    def __post_init__(self):
        attributes = dataclasses.astuple(self)
        # Custom exceptions must always call super(), we use the __post_init__
        # mechanism provided by dataclasses to call the super constructor after
        # this class's __init__ is called.
        super().__init__(*attributes)

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.message}"

    def to_sexp(self):
        error_name = type(self).__name__
        sexp = [error_name]

        for field in dataclasses.fields(self):
            sexp.append(":")
            sexp.append(field.name)

            value = getattr(self, field.name)

            if hasattr(value, fn := "to_sexp"):
                to_sexp = getattr(value, fn)
            elif hasattr(self, fn := f"to_sexp_{field.name}"):
                to_sexp = getattr(self, fn)
            else:

                def to_sexp():
                    return str(value)

            sexp.append(to_sexp())

        return sexp


@dataclass
class InvalidOperationError(CompilerError):
    code = 1

    operator: tuple[str, Span]
    operands: list[tuple[langtypes.Type, Span]]

    def to_sexp_operator(self):
        return [self.operator[0], self.operator[1].to_sexp()]

    def to_sexp_operands(self):
        sexp = []
        for type_, span in self.operands:
            sexp.append([type_.to_sexp(), span.to_sexp()])

        return sexp
