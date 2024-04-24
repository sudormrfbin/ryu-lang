from typing import TYPE_CHECKING, Optional, Sequence

# error_report submodule is generated dynamically by pyo3 on the rust
# side. Hence pyright cannot detect the source file.
from error_report import (  # pyright: ignore [reportMissingModuleSource]
    report_error as ariadne_error,
)


if TYPE_CHECKING:
    from compiler.errors import Span
    import error_report as ariadne


class Text:
    """
    A text is a sequence of strings, some of which can be colored.

    ## Example
    1. To create the text "Hello world" with "world" in a different color:

       ```python
       Text("Hello ", Text.colored("world"))
       ```

    2. To color different spans with the same color, give them the same color_id.
    """

    spans: list["ariadne.MessageSpan"]

    def __init__(self, *args: "ariadne.MessageSpan") -> None:
        self.spans = list(args)

    @staticmethod
    def colored(
        text: str, *, color_id: Optional["ariadne.ColorId"] = None
    ) -> "ariadne.MessageSpan":
        return (text, color_id or text)


class Label:
    """
    Label is an annotated span of the source code that is marked with either
    color, text or both.
    """

    # The three static methods on this class return types that are subtypes
    # of `ariadne.Mark`.

    @staticmethod
    def text(msg: Text, *, span: "Span") -> "ariadne.MarkText":
        return (msg.spans, span.pos())

    @staticmethod
    def color(*, color_id: "ariadne.ColorId", span: "Span") -> "ariadne.MarkColor":
        return (color_id, span.pos())

    @staticmethod
    def colored_text(
        msg: Text, *, color_id: "ariadne.ColorId", span: "Span"
    ) -> "ariadne.MarkTextAndColor":
        return (msg.spans, color_id, span.pos())


Labels = Sequence["ariadne.Mark"]
"""
A list of labels that have been created with the staticmethods on Label

## Example

```python
labels: Labels = [
    Label.text(Message("Type is int"), span=...),
    Label.colored_text(Message("But declared as bool"), span=...),
]
```
"""


def report_error(
    source: str,
    start_pos: int,
    description: Text,
    code: int,
    labels: Labels,
):
    ariadne_error(
        source=source,
        start_pos=start_pos,
        message=description.spans,
        code=code,
        labels=labels,
    )
