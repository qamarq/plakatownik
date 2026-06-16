import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class ProgressEvent:
    step: str
    status: str
    message: str = ""
    elapsed: Optional[float] = None


class ProgressEmitter:
    def __init__(self, sink: Callable[[ProgressEvent], None]):
        self._sink = sink
        self._starty: dict[str, float] = {}

    def started(self, step: str, message: str = "") -> None:
        self._starty[step] = time.perf_counter()
        self._sink(ProgressEvent(step=step, status="started", message=message))

    def done(self, step: str, message: str = "") -> float:
        czas = time.perf_counter() - self._starty.get(step, time.perf_counter())
        self._sink(ProgressEvent(step=step, status="done", message=message, elapsed=czas))
        return czas

    def error(self, step: str, message: str) -> None:
        czas = time.perf_counter() - self._starty.get(step, time.perf_counter())
        self._sink(ProgressEvent(step=step, status="error", message=message, elapsed=czas))
