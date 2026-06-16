from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.jobs import Job, job_manager
from app.schemas import JobStatus, PosterRequest, ProgressEventOut

router = APIRouter()


def _do_statusu(zadanie: Job) -> JobStatus:
    return JobStatus(
        id=zadanie.id,
        status=zadanie.status,
        request=zadanie.request,
        events=[ProgressEventOut(step=e.step, status=e.status, message=e.message, elapsed=e.elapsed) for e in zadanie.zdarzenia],
        error=zadanie.blad,
        result_url=f"/api/posters/{zadanie.id}/file" if zadanie.status == "done" else None,
    )


@router.post("/posters", response_model=JobStatus)
def start_poster(req: PosterRequest):
    zadanie = job_manager.create(req)
    return _do_statusu(zadanie)


@router.get("/posters/{job_id}", response_model=JobStatus)
def get_poster(job_id: str):
    zadanie = job_manager.get(job_id)
    if not zadanie:
        raise HTTPException(404, "Job not found")
    return _do_statusu(zadanie)


@router.get("/posters/{job_id}/file")
def get_poster_file(job_id: str):
    zadanie = job_manager.get(job_id)
    if not zadanie or zadanie.status != "done" or not zadanie.sciezka_wyniku:
        raise HTTPException(404, "Poster not ready")
    return FileResponse(zadanie.sciezka_wyniku)
