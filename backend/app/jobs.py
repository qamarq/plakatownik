import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Optional

from app.config import MAX_CONCURRENT_JOBS
from app.pipeline import generate_poster
from app.progress import ProgressEmitter, ProgressEvent
from app.schemas import PosterRequest

DONE = None


@dataclass
class Job:
    id: str
    request: PosterRequest
    status: str = "queued"
    zdarzenia: list[ProgressEvent] = field(default_factory=list)
    blad: Optional[str] = None
    sciezka_wyniku: Optional[str] = None
    odbiorcy: list[asyncio.Queue] = field(default_factory=list)


class JobManager:
    def __init__(self) -> None:
        self._zadania: dict[str, Job] = {}
        self._executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_JOBS)
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def get(self, job_id: str) -> Optional[Job]:
        return self._zadania.get(job_id)

    def create(self, request: PosterRequest) -> Job:
        zadanie = Job(id=str(uuid.uuid4()), request=request)
        self._zadania[zadanie.id] = zadanie
        self._executor.submit(self._run, zadanie)
        return zadanie

    def subscribe(self, job_id: str) -> asyncio.Queue:
        zadanie = self._zadania[job_id]
        kolejka: asyncio.Queue = asyncio.Queue()
        for zdarzenie in zadanie.zdarzenia:
            kolejka.put_nowait(zdarzenie)
        if zadanie.status in ("done", "error"):
            kolejka.put_nowait(DONE)
        else:
            zadanie.odbiorcy.append(kolejka)
        return kolejka

    def unsubscribe(self, job_id: str, kolejka: asyncio.Queue) -> None:
        zadanie = self._zadania.get(job_id)
        if zadanie and kolejka in zadanie.odbiorcy:
            zadanie.odbiorcy.remove(kolejka)

    def _emit(self, zadanie: Job, zdarzenie: ProgressEvent) -> None:
        zadanie.zdarzenia.append(zdarzenie)
        for kolejka in zadanie.odbiorcy:
            kolejka.put_nowait(zdarzenie)

    def _run(self, zadanie: Job) -> None:
        zadanie.status = "running"

        def sink(zdarzenie: ProgressEvent) -> None:
            self._loop.call_soon_threadsafe(self._emit, zadanie, zdarzenie)

        progress = ProgressEmitter(sink)
        try:
            wynik = generate_poster(zadanie.request, progress)
            zadanie.sciezka_wyniku = str(wynik)
            zadanie.status = "done"
        except Exception as e:
            zadanie.blad = str(e)
            zadanie.status = "error"
        finally:
            self._loop.call_soon_threadsafe(self._finish, zadanie)

    def _finish(self, zadanie: Job) -> None:
        for kolejka in zadanie.odbiorcy:
            kolejka.put_nowait(DONE)
        zadanie.odbiorcy.clear()


job_manager = JobManager()
