from pathlib import Path
from typing import Optional

import matplotlib

# wymagany non-interactive backend, bo render odbywa się w wątku z executora
matplotlib.use("Agg")

import matplotlib.colors as mcolors  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import osmnx as ox  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from networkx import MultiDiGraph  # noqa: E402
from shapely.geometry import Point, box  # noqa: E402

from app.progress import ProgressEmitter

_ZAKRESY_NIELATYNSKIE: tuple[tuple[int, int], ...] = (
    (0x0590, 0x05FF),  # hebrajski
    (0x0600, 0x06FF),  # arabski
    (0x0900, 0x097F),  # dewanagari
    (0x0E00, 0x0E7F),  # tajski
    (0x3040, 0x30FF),  # hiragana/katakana
    (0x3400, 0x4DBF),  # CJK A
    (0x4E00, 0x9FFF),  # CJK
    (0xAC00, 0xD7A3),  # hangul
)


def _uzywa_nielatynskiego_pisma(tekst: str) -> bool:
    litery = [c for c in tekst if c.isalpha()]
    if not litery:
        return False
    nielatynskie = sum(
        1 for c in litery if any(lo <= ord(c) <= hi for lo, hi in _ZAKRESY_NIELATYNSKIE)
    )
    return nielatynskie / len(litery) > 0.5


_POZIOMY_DROG: tuple[tuple[str, ...], ...] = (
    ("motorway", "motorway_link"),
    ("trunk", "trunk_link", "primary", "primary_link"),
    ("secondary", "secondary_link"),
    ("tertiary", "tertiary_link"),
    ("residential", "living_street", "unclassified"),
)
_KOLOR_DLA_POZIOMU = (
    "road_motorway",
    "road_primary",
    "road_secondary",
    "road_tertiary",
    "road_residential",
)
_BAZOWA_SZEROKOSC = 1.4
_SPADEK_NA_POZIOM = 0.8


def _tag_drogi(dane: dict) -> str:
    highway = dane.get("highway", "unclassified")
    return highway[0] if isinstance(highway, list) else highway


def _poziom_drogi(highway: str) -> Optional[int]:
    for indeks, poziom in enumerate(_POZIOMY_DROG):
        if highway in poziom:
            return indeks
    return None


def _style_krawedzi(g: MultiDiGraph, theme: dict) -> tuple[list[str], list[float]]:
    kolory, szerokosci = [], []
    for _, _, dane in g.edges(data=True):
        poziom = _poziom_drogi(_tag_drogi(dane))
        kolory.append(
            theme[_KOLOR_DLA_POZIOMU[poziom]]
            if poziom is not None
            else theme["road_default"]
        )
        glebokosc = poziom if poziom is not None else len(_POZIOMY_DROG)
        szerokosci.append(_BAZOWA_SZEROKOSC * (_SPADEK_NA_POZIOM**glebokosc))
    return kolory, szerokosci


def oblicz_zasieg(promien: float, width: float, height: float) -> tuple[float, float]:
    wspolczynnik = max(width, height) / min(width, height)
    if width >= height:
        return promien * wspolczynnik, promien
    return promien, promien * wspolczynnik


def _okno_kadru(
    g_proj: MultiDiGraph, punkt: tuple[float, float], pol_x: float, pol_y: float
):
    lat, lon = punkt
    srodek = ox.projection.project_geometry(
        Point(lon, lat), crs="EPSG:4326", to_crs=g_proj.graph["crs"]
    )[0]
    minx, miny, maxx, maxy = box(
        srodek.x - pol_x, srodek.y - pol_y, srodek.x + pol_x, srodek.y + pol_y
    ).bounds
    return (minx, maxx), (miny, maxy)


def _pasy_zanikania(ax, color: str, krawedz: str) -> None:
    vals = np.linspace(0, 1, 256).reshape(-1, 1)
    gradient = np.hstack((vals, vals))

    rgb = mcolors.to_rgb(color)
    my_colors = np.zeros((256, 4))
    my_colors[:, 0] = rgb[0]
    my_colors[:, 1] = rgb[1]
    my_colors[:, 2] = rgb[2]

    if krawedz == "bottom":
        my_colors[:, 3] = np.linspace(1, 0, 256)
        extent_y_start = 0.0
        extent_y_end = 0.25
    else:
        my_colors[:, 3] = np.linspace(0, 1, 256)
        extent_y_start = 0.75
        extent_y_end = 1.0

    custom_cmap = mcolors.ListedColormap(my_colors)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    y_range = ylim[1] - ylim[0]
    y_bottom = ylim[0] + y_range * extent_y_start
    y_top = ylim[0] + y_range * extent_y_end

    ax.imshow(
        gradient,
        extent=[xlim[0], xlim[1], y_bottom, y_top],
        aspect="auto",
        cmap=custom_cmap,
        zorder=10,
        origin="lower",
    )


def render_poster(
    g: MultiDiGraph,
    water,
    parks,
    theme: dict,
    fonts: Optional[dict],
    point: tuple[float, float],
    half_x: float,
    half_y: float,
    city: str,
    country: str,
    display_city: Optional[str],
    display_country: Optional[str],
    width: float,
    height: float,
    output_path: Path,
    output_format: str,
    progress: ProgressEmitter,
) -> None:
    display_city = display_city or city
    display_country = display_country or country

    progress.started("render", "Projecting graph and drawing layers")

    fig, ax = plt.subplots(figsize=(width, height), facecolor=theme["bg"])
    ax.set_facecolor(theme["bg"])
    ax.set_position((0.0, 0.0, 1.0, 1.0))

    g_proj = ox.project_graph(g)

    for gdf, kolor, z in ((water, theme["water"], 0.5), (parks, theme["parks"], 0.8)):
        if gdf is None or gdf.empty:
            continue
        poligony = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]
        if not poligony.empty:
            ox.projection.project_gdf(poligony).plot(
                ax=ax, facecolor=kolor, edgecolor="none", zorder=z
            )

    kolory_krawedzi, szerokosci_krawedzi = _style_krawedzi(g_proj, theme)
    ox.plot_graph(
        g_proj,
        ax=ax,
        bgcolor=theme["bg"],
        node_size=0,
        edge_color=kolory_krawedzi,
        edge_linewidth=szerokosci_krawedzi,
        show=False,
        close=False,
    )
    crop_xlim, crop_ylim = _okno_kadru(g_proj, point, half_x, half_y)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(crop_xlim)
    ax.set_ylim(crop_ylim)

    _pasy_zanikania(ax, theme["gradient_color"], krawedz="bottom")
    _pasy_zanikania(ax, theme["gradient_color"], krawedz="top")

    _rysuj_typografie(
        ax, theme, fonts, point, display_city, display_country, width, height
    )

    progress.done("render", f"{len(g_proj.edges)} edges drawn")

    progress.started("save", f"Writing {output_format}")
    fmt = output_format.lower()
    save_kwargs = {"facecolor": theme["bg"], "bbox_inches": "tight", "pad_inches": 0.05}
    if fmt == "png":
        save_kwargs["dpi"] = 300
    plt.savefig(output_path, format=fmt, **save_kwargs)
    plt.close(fig)
    rozmiar_kb = output_path.stat().st_size / 1024
    progress.done("save", f"{rozmiar_kb:.0f} KB")


def _rysuj_typografie(
    ax, theme, fonts, point, display_city, display_country, width, height
):
    skala = min(height, width) / 12.0

    def font(waga: str, rozmiar: float) -> FontProperties:
        return (
            FontProperties(fname=fonts[waga], size=rozmiar)
            if fonts
            else FontProperties(family="monospace", size=rozmiar)
        )

    tytul = (
        display_city
        if _uzywa_nielatynskiego_pisma(display_city)
        else "  ".join(display_city.upper())
    )

    # Dynamiczne dopasowanie rozmiaru tytułu do długości nazwy (jak w oryginale)
    base_adjusted_main = 60 * skala
    if len(display_city) > 10:
        length_factor = 10 / len(display_city)
        rozmiar_tytulu = max(base_adjusted_main * length_factor, 10 * skala)
    else:
        rozmiar_tytulu = base_adjusted_main

    font_tytulu = (
        FontProperties(fname=fonts["bold"], size=rozmiar_tytulu)
        if fonts
        else FontProperties(family="monospace", weight="bold", size=rozmiar_tytulu)
    )

    font_podtytulu = font("light", 22 * skala)
    font_wspolrzednych = font("regular", 14 * skala)
    font_atrybucji = font("light", 8)

    ax.text(
        0.5,
        0.14,
        tytul,
        transform=ax.transAxes,
        color=theme["text"],
        ha="center",
        fontproperties=font_tytulu,
        zorder=11,
    )
    ax.text(
        0.5,
        0.10,
        display_country.upper(),
        transform=ax.transAxes,
        color=theme["text"],
        ha="center",
        fontproperties=font_podtytulu,
        zorder=11,
    )

    lat, lon = point
    wspolrzedne = f"{abs(lat):.4f}° {'N' if lat >= 0 else 'S'} / {abs(lon):.4f}° {'E' if lon >= 0 else 'W'}"
    ax.text(
        0.5,
        0.07,
        wspolrzedne,
        transform=ax.transAxes,
        color=theme["text"],
        alpha=0.7,
        ha="center",
        fontproperties=font_wspolrzednych,
        zorder=11,
    )

    ax.plot(
        [0.4, 0.6],
        [0.125, 0.125],
        transform=ax.transAxes,
        color=theme["text"],
        linewidth=1 * skala,
        zorder=11,
    )

    ax.text(
        0.02,
        0.02,
        "Data: © OpenStreetMap contributors",
        transform=ax.transAxes,
        color=theme["text"],
        alpha=0.5,
        ha="left",
        va="bottom",
        fontproperties=font_atrybucji,
        zorder=11,
    )
