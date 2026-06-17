import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.jobs import job_manager
from app.routes import posters, themes, ws

app = FastAPI(title="Plakatownik")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(themes.router, prefix="/api")
app.include_router(posters.router, prefix="/api")
app.include_router(ws.router)


@app.on_event("startup")
async def on_startup() -> None:
    job_manager.bind_loop(asyncio.get_running_loop())


@app.get("/api/health")
def health():
    return {"status": "ok"}
