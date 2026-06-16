import networkx as nx
import pytest

from app import rendering as r

MOTYW_TESTOWY = {
    "road_motorway": "#111111",
    "road_primary": "#222222",
    "road_secondary": "#333333",
    "road_tertiary": "#444444",
    "road_residential": "#555555",
    "road_default": "#999999",
}


@pytest.mark.parametrize(
    "tekst, oczekiwany",
    [
        ("Tokyo", False),
        ("Wrocław", False),
        ("東京", True),
        ("القاهرة", True),
        ("", False),
    ],
)
def test_uzywa_nielatynskiego_pisma(tekst, oczekiwany):
    assert r._uzywa_nielatynskiego_pisma(tekst) is oczekiwany


def test_oblicz_zasieg_portret():
    pol_x, pol_y = r.oblicz_zasieg(4000, width=12, height=16)
    assert pol_x == 4000
    assert pol_y == pytest.approx(4000 * 16 / 12)


def test_oblicz_zasieg_pejzaz():
    pol_x, pol_y = r.oblicz_zasieg(4000, width=16, height=12)
    assert pol_y == 4000
    assert pol_x == pytest.approx(4000 * 16 / 12)


def _przykladowy_graf():
    g = nx.MultiDiGraph(crs="EPSG:32631")
    g.add_node(1, x=0, y=0)
    g.add_node(2, x=100, y=0)
    g.add_node(3, x=100, y=100)
    g.add_edge(1, 2, highway="motorway")
    g.add_edge(2, 3, highway="footway")
    return g


def test_style_krawedzi_hierarchia():
    g = _przykladowy_graf()
    kolory, szerokosci = r._style_krawedzi(g, MOTYW_TESTOWY)
    assert kolory == ["#111111", "#999999"]
    assert szerokosci[0] > szerokosci[1]


def test_okno_kadru_wymiary():
    g = _przykladowy_graf()
    xlim, ylim = r._okno_kadru(g, (48.85, 2.35), pol_x=1000, pol_y=1500)
    assert xlim[1] - xlim[0] == pytest.approx(2000)
    assert ylim[1] - ylim[0] == pytest.approx(3000)


def test_rozmiar_tytulu_skaluje_z_dlugoscia_tekstu():
    krotki = r._rozmiar_tytulu("Paris", skala=1.0)
    dlugi = r._rozmiar_tytulu("Saint-Petersburg", skala=1.0)
    assert krotki == pytest.approx(60.0)
    assert dlugi < krotki
