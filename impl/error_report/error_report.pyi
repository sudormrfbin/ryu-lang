from typing import Sequence

ColorId = str
MessageSpan = str | tuple[str, ColorId]
Message = list[MessageSpan]

CharSpan = tuple[int, int]

MarkText = tuple[Message, CharSpan]
MarkColor = tuple[ColorId, CharSpan]
MarkTextAndColor = tuple[Message, ColorId, CharSpan]
Mark = MarkText | MarkColor | MarkTextAndColor

def report_error(
    source: str,
    start_pos: int,
    message: Message,
    code: int,
    labels: Sequence[Mark],
) -> None: ...
