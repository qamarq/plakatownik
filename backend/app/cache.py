import pickle

from app.config import CACHE_DIR


class CacheError(Exception):
    pass


def _sciezka_cache(klucz: str):
    bezpieczny = klucz.replace("/", "_").replace("\\", "_")
    return CACHE_DIR / f"{bezpieczny}.pkl"


def cache_get(klucz: str):
    sciezka = _sciezka_cache(klucz)
    if not sciezka.exists():
        return None
    try:
        with open(sciezka, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        raise CacheError(f"Cache read failed for {klucz!r}: {e}") from e


def cache_set(klucz: str, wartosc) -> None:
    sciezka = _sciezka_cache(klucz)
    try:
        with open(sciezka, "wb") as f:
            pickle.dump(wartosc, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        raise CacheError(f"Cache write failed for {klucz!r}: {e}") from e
