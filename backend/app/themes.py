import json

from app.config import THEMES_DIR

MOTYW_DOMYSLNY = {
    "name": "Terracotta",
    "description": "Mediterranean warmth - burnt orange and clay tones on cream",
    "bg": "#F5EDE4",
    "text": "#8B4513",
    "gradient_color": "#F5EDE4",
    "water": "#A8C4C4",
    "parks": "#E8E0D0",
    "road_motorway": "#A0522D",
    "road_primary": "#B8653A",
    "road_secondary": "#C9846A",
    "road_tertiary": "#D9A08A",
    "road_residential": "#E5C4B0",
    "road_default": "#D9A08A",
}


def list_theme_ids() -> list[str]:
    return sorted(p.stem for p in THEMES_DIR.glob("*.json"))


def list_themes() -> list[dict]:
    podsumowania = []
    for theme_id in list_theme_ids():
        motyw = load_theme(theme_id)
        podsumowania.append(
            {
                "id": theme_id,
                "name": motyw.get("name", theme_id),
                "description": motyw.get("description", ""),
                "bg": motyw["bg"],
                "text": motyw["text"],
                "road_primary": motyw["road_primary"],
                "water": motyw["water"],
            }
        )
    return podsumowania


def load_theme(theme_id: str) -> dict:
    sciezka = THEMES_DIR / f"{theme_id}.json"
    if not sciezka.exists():
        return MOTYW_DOMYSLNY
    with open(sciezka, "r", encoding="utf-8") as f:
        return json.load(f)
