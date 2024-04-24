from typing import Any
import typing
import dataclasses
from dataclasses import dataclass

from compiler.lalr import Meta as LarkMeta


from compiler import errors

SKIP_SERIALIZE = "skip_serialize"
AstDict = dict[typing.Type["Ast"], dict[str, Any]]


@dataclass
class Ast:
    # InitVar makes meta available on the __post_init__ method
    # and excludes it in the generated __init__.
    meta: dataclasses.InitVar[LarkMeta]
    """Line and column numbers from lark framework.
    Converted to Span for strorage within the class."""

    span: errors.Span = dataclasses.field(init=False, metadata={SKIP_SERIALIZE: True})
    """Line and column number information."""

    def __post_init__(self, meta: LarkMeta):
        self.span = errors.Span.from_meta(meta)

    def to_dict(self) -> AstDict:
        attrs: dict[str, Any] = {}

        for field in dataclasses.fields(self):
            if SKIP_SERIALIZE in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, Ast):
                attrs[field.name] = value.to_dict()
            elif isinstance(value, list):
                match value:
                    case []:
                        attrs[field.name] = []
                    case [Ast(), *_]:  # type: ignore
                        attrs[field.name] = [v.to_dict() for v in value]  # type: ignore
                    case _:  # type: ignore
                        pass
            elif value is not None:
                attrs[field.name] = value

        return {type(self): attrs}

    def to_type_dict(self) -> dict[Any, Any]:
        attrs = {}

        if ty := getattr(self, "type", None):
            attrs["type"] = type(ty)

        fields = attrs["fields"] = {}

        for field in dataclasses.fields(self):
            if SKIP_SERIALIZE in field.metadata:
                continue

            value = getattr(self, field.name)
            if isinstance(value, Ast):
                fields[field.name] = value.to_type_dict()
            elif isinstance(value, list):
                match value:
                    case []:
                        fields[field.name] = []
                    case [Ast(), *_]:  # type: ignore
                        fields[field.name] = [v.to_type_dict() for v in value]  # type: ignore
                    case _:  # type: ignore
                        pass

        return {type(self): attrs}
