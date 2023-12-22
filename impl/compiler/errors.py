from typing import Iterable


class CompilerError(Exception):
    _SEXP_INCLUDE: Iterable[str]

    def to_sexp(self):
        error_name = type(self).__name__
        sexp = [error_name]

        for arg in self._SEXP_INCLUDE:
            sexp.append(":")
            sexp.append(arg)
            sexp.append(str(getattr(self, arg)))

        return sexp


class InvalidOperationError(CompilerError):
    _SEXP_INCLUDE = ("message",)

    def __init__(self, message: str):
        super().__init__(message)

        self.message = message
