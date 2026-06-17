import time

from geopy.geocoders import Nominatim

from app.cache import CacheError, cache_get, cache_set
from app.progress import ProgressEmitter


def get_coordinates(city: str, country: str, progress: ProgressEmitter) -> tuple[float, float]:
    klucz = f"coords_{city.lower()}_{country.lower()}"
    cached = cache_get(klucz)
    if cached:
        progress.done("geocode", f"{cached[0]:.4f}, {cached[1]:.4f} (cached)")
        return cached

    progress.started("geocode", f"Looking up {city}, {country} via Nominatim")
    geolokator = Nominatim(user_agent="plakatownik", timeout=10)
    time.sleep(1)

    try:
        lokalizacja = geolokator.geocode(f"{city}, {country}")
    except Exception as e:
        progress.error("geocode", f"Geocoding failed: {e}")
        raise ValueError(f"Geocoding failed for {city}, {country}: {e}") from e

    if not lokalizacja:
        progress.error("geocode", "City not found")
        raise ValueError(f"Could not find coordinates for {city}, {country}")

    punkt = (lokalizacja.latitude, lokalizacja.longitude)
    try:
        cache_set(klucz, punkt)
    except CacheError:
        pass

    progress.done("geocode", f"{punkt[0]:.4f}, {punkt[1]:.4f}")
    return punkt
