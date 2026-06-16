from fastapi import APIRouter

from app.schemas import ThemeSummary
from app.themes import list_themes

router = APIRouter()


@router.get("/themes", response_model=list[ThemeSummary])
def get_themes():
    return list_themes()
