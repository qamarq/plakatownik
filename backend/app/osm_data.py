from typing import cast

import osmnx as ox
from geopandas import GeoDataFrame
from networkx import MultiDiGraph

from app.cache import CacheError, cache_get, cache_set
from app.config import OVERPASS_URL
from app.progress import ProgressEmitter

ox.settings.overpass_url = OVERPASS_URL
ox.settings.log_console = True

TAGI_WODY = {"natural": ["water", "bay", "strait", "wetland"], "waterway": "riverbank"}
TAGI_ZIELENI = {"leisure": ["park", "garden"], "landuse": ["grass", "forest"]}


def fetch_graph(point: tuple[float, float], promien: float) -> MultiDiGraph:
    lat, lon = point
    klucz = f"graph_{lat}_{lon}_{promien}_all"
    cached = cache_get(klucz)
    if cached is not None:
        return cast(MultiDiGraph, cached)

    g = ox.graph_from_point(point, dist=promien, dist_type="bbox", network_type="all", truncate_by_edge=True)
    try:
        cache_set(klucz, g)
    except CacheError:
        pass
    return g


def fetch_features(point: tuple[float, float], promien: float, tags: dict, nazwa: str) -> GeoDataFrame | None:
    lat, lon = point
    tag_str = "_".join(tags.keys())
    klucz = f"{nazwa}_{lat}_{lon}_{promien}_{tag_str}"
    cached = cache_get(klucz)
    if cached is not None:
        return cast(GeoDataFrame, cached)

    try:
        dane = ox.features_from_point(point, tags=tags, dist=promien)
    except Exception:
        return None

    try:
        cache_set(klucz, dane)
    except CacheError:
        pass
    return dane


def fetch_all(point: tuple[float, float], promien: float, progress: ProgressEmitter):
    progress.started("fetch_graph", f"Requesting street network (dist={promien:.0f}m)")
    g = fetch_graph(point, promien)
    progress.done("fetch_graph", f"{len(g.edges)} edges, {len(g.nodes)} nodes")

    progress.started("fetch_water", "Requesting water features")
    woda = fetch_features(point, promien, TAGI_WODY, "water")
    progress.done("fetch_water", f"{len(woda)} features" if woda is not None else "none found")

    progress.started("fetch_parks", "Requesting parks/green spaces")
    zielen = fetch_features(point, promien, TAGI_ZIELENI, "parks")
    progress.done("fetch_parks", f"{len(zielen)} features" if zielen is not None else "none found")

    return g, woda, zielen
