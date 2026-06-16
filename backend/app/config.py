import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CACHE_DIR = Path(os.environ.get("CACHE_DIR", BASE_DIR / "data" / "cache"))
POSTERS_DIR = Path(os.environ.get("POSTERS_DIR", BASE_DIR / "data" / "posters"))
THEMES_DIR = Path(os.environ.get("THEMES_DIR", BASE_DIR / "themes"))
FONTS_DIR = Path(os.environ.get("FONTS_DIR", BASE_DIR / "fonts"))

CACHE_DIR.mkdir(parents=True, exist_ok=True)
POSTERS_DIR.mkdir(parents=True, exist_ok=True)

OVERPASS_URL = os.environ.get("OVERPASS_URL", "https://overpass-api.de/api")
MAX_CONCURRENT_JOBS = int(os.environ.get("MAX_CONCURRENT_JOBS", "2"))

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
