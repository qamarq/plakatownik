import re
from datetime import datetime
from pathlib import Path

from app.config import POSTERS_DIR
from app.fonts import load_fonts
from app.geocode import get_coordinates
from app.osm_data import fetch_all
from app.progress import ProgressEmitter
from app.rendering import oblicz_zasieg, render_poster
from app.schemas import PosterRequest
from app.themes import load_theme

_MARGINES_POBIERANIA = 1.08


def _nazwa_pliku(req: PosterRequest) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "_", req.city.lower()).strip("_")
    znacznik_czasu = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return POSTERS_DIR / f"{slug}_{req.theme}_{znacznik_czasu}.{req.format}"


def generate_poster(req: PosterRequest, progress: ProgressEmitter) -> Path:
    if req.latitude is not None and req.longitude is not None:
        punkt = (req.latitude, req.longitude)
        progress.started("geocode", "Using provided coordinates")
        progress.done("geocode", f"{punkt[0]:.4f}, {punkt[1]:.4f}")
    else:
        punkt = get_coordinates(req.city, req.country, progress)

    theme = load_theme(req.theme)
    fonts = load_fonts(req.font_family)

    pol_x, pol_y = oblicz_zasieg(req.distance, req.width, req.height)
    promien_pobierania = max(pol_x, pol_y) * _MARGINES_POBIERANIA

    g, water, parks = fetch_all(punkt, promien_pobierania, progress)

    sciezka_wyjsciowa = _nazwa_pliku(req)
    render_poster(
        g=g,
        water=water,
        parks=parks,
        theme=theme,
        fonts=fonts,
        point=punkt,
        half_x=pol_x,
        half_y=pol_y,
        city=req.city,
        country=req.country,
        display_city=req.display_city,
        display_country=req.display_country or req.country_label,
        width=req.width,
        height=req.height,
        output_path=sciezka_wyjsciowa,
        output_format=req.format,
        progress=progress,
    )
    return sciezka_wyjsciowa
