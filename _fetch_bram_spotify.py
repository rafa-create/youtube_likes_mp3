"""Fetch Bram Spotify playlist via embed token + Web API, build bram_profile.json."""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

PLAYLIST_ID = "7prdtzDctYFscp8PgFsp6i"
PLAYLIST_URL = f"https://open.spotify.com/playlist/{PLAYLIST_ID}"
EMBED_URL = f"https://open.spotify.com/embed/playlist/{PLAYLIST_ID}"
OUT = Path(__file__).resolve().parent / "bram_profile.json"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

FR_HINTS = re.compile(
    r"\b(le|la|les|des|une|mon|ma|mes|pour|avec|sans|dans|sur|je|tu|nous|"
    r"amour|chanson|vie|nuit|soleil|coeur|cœur)\b",
    re.I,
)
ES_HINTS = re.compile(
    r"\b(el|los|las|que|por|para|amor|vida|noche|corazon|corazón|"
    r"danza|mar|buscando|andaba)\b|"
    r"\b(enrique|iglesias|shakira|edu requejo|koino)\b",
    re.I,
)

STYLE_RULES = [
    (
        "acoustic / folk / island",
        re.compile(
            r"jack johnson|donavon frankenreiter|beautiful girls|bahamas|"
            r"john mayer|john cruz|bobby alu|\balo\b|eddie vedder|"
            r"ben harper|xavier rudd|surf|acoustic|banana pancakes|"
            r"seasick|big wave|love song|subplots|captain is drunk",
            re.I,
        ),
    ),
    (
        "blues / roots",
        re.compile(
            r"keb.?mo|taj mahal|chris stapleton|josh teskey|ash grunwald|"
            r"blues|tennessee whiskey|gary clark|brianna harness|"
            r"push the blues",
            re.I,
        ),
    ),
    (
        "soul / r&b soft",
        re.compile(
            r"michael kiwanuka|jeangu|jose gonzalez|jos[eé] gonz[aá]lez|"
            r"bobby mcferrin|heartbeats|home again|macrooy",
            re.I,
        ),
    ),
    (
        "indie / soft rock",
        re.compile(r"\bbeck\b|wow\b|letter to|coldplay|passenger", re.I),
    ),
    (
        "latin / world",
        re.compile(
            r"edu requejo|koino yokan|lo que|la danza|la mar|"
            r"spanish|latino|bossa|reggae|hawaiian|mana maoli",
            re.I,
        ),
    ),
]


def http_get(url: str, headers: dict | None = None) -> bytes:
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read()


def get_token_from_embed() -> str:
    html = http_get(EMBED_URL).decode("utf-8", "replace")
    m = re.search(r'"accessToken":"([^"]+)"', html)
    if not m:
        raise RuntimeError("No accessToken in Spotify embed page")
    return m.group(1)


def api_get(url: str, token: str) -> dict:
    try:
        raw = http_get(url, headers={"Authorization": f"Bearer {token}"})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"API {e.code} {url}: {body[:300]}") from e
    return json.loads(raw.decode("utf-8", "replace"))


def fetch_playlist(token: str) -> tuple[dict, list[dict]]:
    meta = api_get(
        f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}"
        "?fields=name,description,owner(display_name),tracks(total),followers",
        token,
    )
    tracks: list[dict] = []
    url = (
        f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
        "?limit=100&fields=items(added_at,track(id,name,duration_ms,"
        "artists(name),album(name),preview_url)),next"
    )
    while url:
        page = api_get(url, token)
        for item in page.get("items") or []:
            t = item.get("track") or {}
            if not t or not t.get("name"):
                continue
            artists = [
                a.get("name") for a in (t.get("artists") or []) if a.get("name")
            ]
            tracks.append(
                {
                    "id": t.get("id"),
                    "name": t["name"],
                    "artists": artists,
                    "artist": ", ".join(artists),
                    "album": (t.get("album") or {}).get("name"),
                    "duration_ms": t.get("duration_ms"),
                    "preview_url": t.get("preview_url"),
                    "added_at": item.get("added_at"),
                }
            )
        url = page.get("next")
        time.sleep(0.12)
    return meta, tracks


def detect_language(title: str, artist: str) -> str:
    blob = f"{title} {artist}"
    if ES_HINTS.search(blob) or re.search(r"[ñ¿¡]", blob):
        return "es"
    if FR_HINTS.search(blob) or re.search(r"[àâäéèêëïîôùûüç]", blob):
        # accents alone can be Spanish too — prefer ES rules first
        if re.search(r"\b(el|los|la danza|mar)\b", blob, re.I):
            return "es"
        return "fr"
    return "en"


def detect_styles(title: str, artist: str) -> list[str]:
    blob = f"{title} {artist}"
    hits = [name for name, rx in STYLE_RULES if rx.search(blob)]
    return hits or ["chill / soft pop"]


def build_profile(meta: dict, tracks: list[dict]) -> dict:
    artists: Counter[str] = Counter()
    langs: Counter[str] = Counter()
    styles: Counter[str] = Counter()
    durations = []

    for t in tracks:
        for a in t["artists"]:
            artists[a] += 1
        lang = detect_language(t["name"], t["artist"])
        t["language"] = lang
        langs[lang] += 1
        st = detect_styles(t["name"], t["artist"])
        t["styles"] = st
        for s in st:
            styles[s] += 1
        if t.get("duration_ms"):
            durations.append(t["duration_ms"] / 1000.0)

    creation_recipes = [
        {
            "chords": "G–C–D–Em",
            "degrees": "I–IV–V–vi",
            "bpm_median": 92,
            "tempo_bucket": "80–100 mid lent",
            "language": "en",
            "key": "G major / E minor",
            "instrument": "guitare acoustique fingerstyle",
            "why": "Cœur Jack Johnson / Frankenreiter / island-folk de la playlist",
            "recipe": (
                "Écrire autour de G–C–D–Em (~I–IV–V–vi) · ~90–95 BPM · EN · "
                "guitare fingerstyle + voix soft"
            ),
        },
        {
            "chords": "C–G–Am–F",
            "degrees": "I–V–vi–IV",
            "bpm_median": 88,
            "tempo_bucket": "80–100 mid lent",
            "language": "en",
            "key": "C major",
            "instrument": "guitare nylon / steel + voix",
            "why": "Soft pop / Mayer acoustic / campfire",
            "recipe": (
                "Écrire autour de C–G–Am–F (~I–V–vi–IV) · ~85–95 BPM · EN · "
                "voix douce"
            ),
        },
        {
            "chords": "Am–G–C–F",
            "degrees": "vi–V–I–IV",
            "bpm_median": 78,
            "tempo_bucket": "<80 ballade",
            "language": "en",
            "key": "A minor",
            "instrument": "guitare + harmonica / soul voice",
            "why": "Blues-soul (Kiwanuka, Stapleton, Teskey, Keb' Mo')",
            "recipe": "Écrire autour de Am–G–C–F · ~70–85 BPM · EN · blues / soul soft",
        },
        {
            "chords": "Dm–Bb–F–C",
            "degrees": "i–bVI–bIII–bVII",
            "bpm_median": 96,
            "tempo_bucket": "80–100 mid lent",
            "language": "es",
            "key": "D minor",
            "instrument": "guitare + percussions light",
            "why": "Poche latin / world de la playlist",
            "recipe": "Écrire autour de Dm–Bb–F–C · ~90–100 BPM · ES · groove léger",
        },
    ]

    dur_med = sorted(durations)[len(durations) // 2] if durations else None

    return {
        "source": PLAYLIST_URL,
        "name": meta.get("name") or "Chill",
        "owner": (meta.get("owner") or {}).get("display_name") or "Bram van Beurden",
        "track_count": len(tracks),
        "spotify_total": (meta.get("tracks") or {}).get("total"),
        "followers": (meta.get("followers") or {}).get("total"),
        "description": meta.get("description") or "",
        "duration_median_sec": round(dur_med, 1) if dur_med else None,
        "top_artists": [{"name": n, "count": c} for n, c in artists.most_common(15)],
        "languages": [{"name": k, "count": v} for k, v in langs.most_common()],
        "style_signals": [{"name": k, "count": v} for k, v in styles.most_common()],
        "instruments_likely": [
            {
                "name": "guitare acoustique",
                "share_pct": 55,
                "note": "Jack Johnson / Frankenreiter / Mayer",
            },
            {
                "name": "voix soft / lead",
                "share_pct": 40,
                "note": "presque toute la playlist est chantée",
            },
            {
                "name": "harmonica / blues harp",
                "share_pct": 12,
                "note": "blues / roots pocket",
            },
            {
                "name": "ukulele / percussions light",
                "share_pct": 10,
                "note": "island / chill vibe",
            },
            {
                "name": "piano / soft keys",
                "share_pct": 8,
                "note": "ballades / soul",
            },
        ],
        "tempo_profile": {
            "median_estimate": 90,
            "p25_estimate": 78,
            "p75_estimate": 102,
            "buckets": [
                {"name": "<80 ballade", "count_label": "élevé"},
                {"name": "80–100 mid lent", "count_label": "dominant"},
                {"name": "100–120 pop", "count_label": "faible"},
                {"name": "120+", "count_label": "rare"},
            ],
            "note": (
                "Estimations curatorielles (pas d'analyse audio complète) — "
                "chill / acoustic ~80–100 BPM."
            ),
        },
        "creation_recipes": creation_recipes,
        "insights": [
            f"Playlist « {meta.get('name') or 'Chill'} » de Bram · {len(tracks)} titres.",
            "Artistes phares : "
            + ", ".join(f"{a} ({c})" for a, c in artists.most_common(5))
            + ".",
            "Langues (heuristique) : "
            + ", ".join(f"{k} ({v})" for k, v in langs.most_common())
            + ".",
            "Centre : acoustic island-folk / soft blues · guitare · EN · ~90 BPM.",
            "Cible création #1 : G–C–D–Em · fingerstyle · voix soft EN.",
        ],
        "sample_tracks": [
            {
                "name": t["name"],
                "artist": t["artist"],
                "language": t["language"],
                "styles": t["styles"],
            }
            for t in tracks[:50]
        ],
        "method": (
            "Spotify Web API (token embed open.spotify.com) + heuristiques "
            "artistes/titres ; recettes accords/tempo curatorielles pour ce "
            "catalogue chill/acoustic — pas de librosa sur MP3."
        ),
    }


def main() -> None:
    if hasattr(__import__("sys").stdout, "reconfigure"):
        __import__("sys").stdout.reconfigure(encoding="utf-8", errors="replace")
    print("Token from embed…")
    token = get_token_from_embed()
    print("Fetch playlist…")
    meta, tracks = fetch_playlist(token)
    print(f"Got {len(tracks)} / meta total {meta.get('tracks')}")
    profile = build_profile(meta, tracks)
    OUT.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print("Top:", profile["top_artists"][:8])
    print("Langs:", profile["languages"])
    print("Styles:", profile["style_signals"][:6])


if __name__ == "__main__":
    main()
