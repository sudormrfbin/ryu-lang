ColorId = str
MessageSpan = str | tuple[str, ColorId]
Message = list[MessageSpan]

def report_error(
    source: str,
    start_pos: int,
    message: Message,
    code: int,
    labels: list[tuple[Message, tuple[int, int]]],
): ...
