import re
import requests

def normalize_track_id(track_id) -> str:
    if track_id is None:
        return ""
    s = str(track_id).strip()

    if s.endswith(".0"):
        s = s[:-2]

    s = re.sub(r"\D", "", s)
    return s

def parse_apple(track_id: str, country="us", lang="en"):
    url = "https://itunes.apple.com/lookup"
    tid = normalize_track_id(track_id)
    if not tid:
        raise ValueError(f"Invalid Apple track_id: {track_id}")

    params = {"id": tid, "country": country, "lang": lang}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    if data.get("resultCount", 0) < 1:
        raise ValueError(f"Apple app not found for track_id={tid}")

    return data["results"][0]

def apple_to_row(a: dict) -> dict:
    apple_id = str(a.get("trackId", "") or "")

    shots = []
    shots += a.get("screenshotUrls") or []
    shots += a.get("ipadScreenshotUrls") or []

    icon = (
        a.get("artworkUrl512")
        or a.get("artworkUrl100")
        or a.get("artworkUrl60")
        or ""
    )

    release = a.get("releaseDate") or ""
    if release:
        release = release[:10]  # YYYY-MM-DD

    genre = a.get("primaryGenreName") or ""
    if not genre:
        genres = a.get("genres") or []
        genre = genres[0] if genres else ""

    return {
        "apple_id": apple_id,
        "title": a.get("trackName", "") or "",
        "genre": genre,
        "release_date": release,
        "url": a.get("trackViewUrl", "") or "",
        "icon": icon,
        "screenshots": shots,
    }

