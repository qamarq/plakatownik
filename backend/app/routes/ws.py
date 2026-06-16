from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.jobs import DONE, job_manager

router = APIRouter()


@router.websocket("/ws/posters/{job_id}")
async def poster_progress(websocket: WebSocket, job_id: str) -> None:
    zadanie = job_manager.get(job_id)
    if not zadanie:
        await websocket.close(code=4404)
        return

    await websocket.accept()
    kolejka = job_manager.subscribe(job_id)
    try:
        while True:
            zdarzenie = await kolejka.get()
            if zdarzenie is DONE:
                result_url = f"/api/posters/{zadanie.id}/file" if zadanie.status == "done" else None
                await websocket.send_json(
                    {"step": "complete", "status": zadanie.status, "error": zadanie.blad, "result_url": result_url}
                )
                break
            await websocket.send_json(
                {"step": zdarzenie.step, "status": zdarzenie.status, "message": zdarzenie.message, "elapsed": zdarzenie.elapsed}
            )
    except WebSocketDisconnect:
        pass
    finally:
        job_manager.unsubscribe(job_id, kolejka)
