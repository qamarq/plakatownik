from typing import Optional

from pydantic import BaseModel, Field


class PosterRequest(BaseModel):
    city: str
    country: str
    theme: str = "terracotta"
    distance: int = Field(
        4000,
        ge=500,
        le=20000,
        description="Half-extent in meters guaranteed visible along the poster's shorter side",
    )
    width: float = Field(12, gt=0, le=20)
    height: float = Field(16, gt=0, le=20)
    format: str = Field("png", pattern="^(png|svg|pdf)$")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_label: Optional[str] = None
    display_city: Optional[str] = None
    display_country: Optional[str] = None
    font_family: Optional[str] = None


class ProgressEventOut(BaseModel):
    step: str
    status: str
    message: str = ""
    elapsed: Optional[float] = None


class JobStatus(BaseModel):
    id: str
    status: str  # "queued" | "running" | "done" | "error"
    request: PosterRequest
    events: list[ProgressEventOut] = []
    error: Optional[str] = None
    result_url: Optional[str] = None


class ThemeSummary(BaseModel):
    id: str
    name: str
    description: str = ""
    bg: str
    text: str
    road_primary: str
    water: str
