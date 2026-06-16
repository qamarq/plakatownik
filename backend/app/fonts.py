import re
from pathlib import Path
from typing import Optional

import requests

from app.config import FONTS_DIR

KATALOG_CACHE_FONTOW = FONTS_DIR / "cache"

WAGI = {300: "light", 400: "regular", 700: "bold"}


def _pobierz_google_font(rodzina: str) -> Optional[dict]:
    KATALOG_CACHE_FONTOW.mkdir(parents=True, exist_ok=True)
    nazwa_bezpieczna = rodzina.replace(" ", "_").lower()
    wagi = list(WAGI)

    try:
        odpowiedz = requests.get(
            "https://fonts.googleapis.com/css2",
            params={"family": f"{rodzina}:wght@{';'.join(map(str, wagi))}"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        odpowiedz.raise_for_status()

        mapa_url = {}
        for blok in re.split(r"@font-face\s*\{", odpowiedz.text)[1:]:
            dopasowanie_wagi = re.search(r"font-weight:\s*(\d+)", blok)
            dopasowanie_url = re.search(r"url\((https://[^)]+\.(?:woff2|ttf))\)", blok)
            if dopasowanie_wagi and dopasowanie_url:
                mapa_url[int(dopasowanie_wagi.group(1))] = dopasowanie_url.group(1)

        pliki = {}
        for waga, klucz in WAGI.items():
            url = mapa_url.get(waga) or next(iter(mapa_url.values()), None)
            if not url:
                continue
            rozszerzenie = "woff2" if url.endswith(".woff2") else "ttf"
            sciezka = KATALOG_CACHE_FONTOW / f"{nazwa_bezpieczna}_{klucz}.{rozszerzenie}"
            if not sciezka.exists():
                odpowiedz_pliku = requests.get(url, timeout=10)
                odpowiedz_pliku.raise_for_status()
                sciezka.write_bytes(odpowiedz_pliku.content)
            pliki[klucz] = str(sciezka)

        for klucz in ("regular", "bold", "light"):
            if klucz not in pliki and pliki:
                pliki[klucz] = next(iter(pliki.values()))

        return pliki or None
    except Exception:
        return None


def load_fonts(font_family: Optional[str] = None) -> Optional[dict]:
    if font_family and font_family.lower() != "roboto":
        czcionki = _pobierz_google_font(font_family)
        if czcionki:
            return czcionki

    czcionki = {
        "bold": str(FONTS_DIR / "Roboto-Bold.ttf"),
        "regular": str(FONTS_DIR / "Roboto-Regular.ttf"),
        "light": str(FONTS_DIR / "Roboto-Light.ttf"),
    }
    if all(Path(p).exists() for p in czcionki.values()):
        return czcionki
    return None
