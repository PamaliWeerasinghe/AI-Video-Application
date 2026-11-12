import builtins
import io
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Callable, Iterator, TextIO


_output_sink: ContextVar[Callable[[str], None] | None] = ContextVar(
    "agent_output_sink", default=None
)


@contextmanager
def capture_agent_output(sink: Callable[[str], None]) -> Iterator[None]:
    token = _output_sink.set(sink)
    try:
        yield
    finally:
        _output_sink.reset(token)


def agent_print(
    *values: object,
    sep: str | None = " ",
    end: str | None = "\n",
    file: TextIO | None = None,
    flush: bool = False,
) -> None:
    sink = _output_sink.get()
    if sink is None or file is not None:
        builtins.print(*values, sep=sep, end=end, file=file, flush=flush)
        return

    output = io.StringIO()
    builtins.print(*values, sep=sep, end=end, file=output, flush=flush)
    sink(output.getvalue())
