"""Analyze liked music: meta patterns + audio key/BPM sample."""
from __future__ import annotations

import json
import re
import sys
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
MP3_DIR = ROOT / "mp3"
PLAYLIST = ROOT / "_playlist.tsv"
OUT = ROOT / "music_profile.json"

# Krumhansl-Schmuckler key profiles
MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

GENRE_RULES = [
    ("piano / neo-classical", ["einaudi", "piano", "gibran alcocer", "ludovico", "yiruma", "neoclassical"]),
    ("electronic / EDM", ["alan walker", "remix", "avicci", "tiesto", "martin garrix", "monstercat", "edm", "dubstep"]),
    ("hip-hop / rap", ["rap", "hip hop", "hip-hop", "6ix9ine", "boomin", "drill"]),
    ("pop", ["taylor swift", "adele", "sia", "charlie puth", "mika", "angele", "pomme"]),
    ("rock / alternative", ["pink floyd", "imagine dragons", "lumineers", "rock", "nirvana"]),
    ("latin / reggaeton", ["ozuna", "anuel", "reggaeton", "bachata", "despeinada", "enrique iglesias"]),
    ("french chanson / pop FR", ["pomme", "boulevard des airs", "stephan eicher", "tragédie", "bigflo", "oli", "l.e.j", "2frères", "adèle castillon"]),
    ("cinematic / soundtrack", ["hans zimmer", "soundtrack", "gladiator", "film music", "bandas sonoras"]),
    ("folk / acoustic", ["john denver", "acoustic", "folk", "guitar cover", "fingerstyle"]),
    ("ambient / chill", ["relax", "sleep", "chill", "ambient", "meditation", "417hz", "tibetan"]),
]


def split_artist_title(raw: str) -> tuple[str, str]:
    raw = raw.strip()
    if " - " in raw:
        a, t = raw.split(" - ", 1)
        return a.strip(), t.strip()
    if " – " in raw:
        a, t = raw.split(" – ", 1)
        return a.strip(), t.strip()
    return "", raw


def guess_genres(text: str) -> list[str]:
    low = text.casefold()
    hits = []
    for name, keys in GENRE_RULES:
        if any(k in low for k in keys):
            hits.append(name)
    return hits or ["autre / non classé"]


def estimate_key(y: np.ndarray, sr: int) -> tuple[str, str, float]:
    import librosa

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_avg = chroma.mean(axis=1)
    if chroma_avg.sum() == 0:
        return "?", "?", 0.0
    chroma_avg = chroma_avg / (chroma_avg.sum() + 1e-9)

    best_score = -1e9
    best = ("C", "major", 0.0)
    for i in range(12):
        maj = np.corrcoef(chroma_avg, np.roll(MAJOR, i))[0, 1]
        minr = np.corrcoef(chroma_avg, np.roll(MINOR, i))[0, 1]
        if maj > best_score:
            best_score = maj
            best = (NOTES[i], "major", float(maj))
        if minr > best_score:
            best_score = minr
            best = (NOTES[i], "minor", float(minr))
    return best


def analyze_audio(path: Path, duration: float = 90.0) -> dict | None:
    import librosa

    try:
        y, sr = librosa.load(str(path), sr=22050, mono=True, duration=duration)
        if len(y) < sr * 5:
            return None
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if isinstance(tempo, np.ndarray):
            tempo = float(tempo[0]) if tempo.size else 0.0
        else:
            tempo = float(tempo)
        key, mode, conf = estimate_key(y, sr)
        return {
            "file": path.name,
            "bpm": round(tempo, 1),
            "key": key,
            "mode": mode,
            "key_confidence": round(conf, 3),
        }
    except Exception as exc:
        return {"file": path.name, "error": str(exc)}


def bpm_bucket(bpm: float) -> str:
    if bpm < 70:
        return "<70 (très lent)"
    if bpm < 90:
        return "70–90 (lent / ballade)"
    if bpm < 110:
        return "90–110 (midtempo)"
    if bpm < 130:
        return "110–130 (pop / groove)"
    if bpm < 150:
        return "130–150 (dance / uptempo)"
    return "150+ (rapide / EDM)"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # --- Meta from playlist ---
    titles: list[str] = []
    if PLAYLIST.is_file():
        for line in PLAYLIST.read_text(encoding="utf-8").splitlines():
            if "\t" not in line:
                continue
            _, title = line.split("\t", 1)
            titles.append(title.strip())

    artists: Counter[str] = Counter()
    genres: Counter[str] = Counter()
    for title in titles:
        artist, _ = split_artist_title(title)
        if artist:
            # normalize featured artists: take first name before "," or " x " or "&" sometimes keep full
            base = re.split(r"\s+(?:feat\.?|ft\.?|×|x)\s+", artist, flags=re.I)[0].strip()
            if len(base) > 1:
                artists[base] += 1
        for g in guess_genres(title):
            genres[g] += 1

    # --- Audio sample ---
    files = sorted(MP3_DIR.glob("*.mp3"))
    # Prefer diverse sample: every Nth file + first 20
    sample_size = min(80, len(files))
    if len(files) <= sample_size:
        sample = files
    else:
        step = max(1, len(files) // sample_size)
        sample = files[::step][:sample_size]

    print(f"Audio sample: {len(sample)} / {len(files)} files")
    audio_rows = []
    for i, f in enumerate(sample, 1):
        print(f"[{i}/{len(sample)}] {f.name[:60]}")
        row = analyze_audio(f)
        if row and "error" not in row:
            audio_rows.append(row)

    key_counts = Counter(f"{r['key']} {r['mode']}" for r in audio_rows)
    mode_counts = Counter(r["mode"] for r in audio_rows)
    bpm_counts = Counter(bpm_bucket(r["bpm"]) for r in audio_rows)
    bpms = [r["bpm"] for r in audio_rows if r["bpm"] > 0]

    # Common relative patterns (heuristic narrative)
    maj = mode_counts.get("major", 0)
    minor = mode_counts.get("minor", 0)
    top_keys = key_counts.most_common(8)
    top_artists = artists.most_common(15)
    top_genres = genres.most_common(10)

    profile = {
        "playlist_count": len(titles),
        "mp3_count": len(files),
        "audio_sample_size": len(audio_rows),
        "top_artists": [{"name": n, "count": c} for n, c in top_artists],
        "genre_signals": [{"name": n, "count": c} for n, c in top_genres],
        "modes": [{"name": n, "count": c} for n, c in mode_counts.most_common()],
        "keys": [{"name": n, "count": c} for n, c in top_keys],
        "bpm_buckets": [{"name": n, "count": c} for n, c in bpm_counts.most_common()],
        "bpm_stats": {
            "mean": round(float(np.mean(bpms)), 1) if bpms else None,
            "median": round(float(np.median(bpms)), 1) if bpms else None,
            "p25": round(float(np.percentile(bpms, 25)), 1) if bpms else None,
            "p75": round(float(np.percentile(bpms, 75)), 1) if bpms else None,
        },
        "sample_tracks": audio_rows[:25],
        "insights": [],
    }

    insights = []
    if minor + maj:
        ratio = minor / (minor + maj)
        if ratio >= 0.55:
            insights.append(
                f"Dominance mineure (~{ratio:.0%}) : couleurs mélancoliques / introspectives plus que joyeuses."
            )
        elif ratio <= 0.4:
            insights.append(
                f"Dominance majeure (~{1-ratio:.0%}) : plutôt clair, pop / uplift."
            )
        else:
            insights.append("Équilibre majeur/mineur : tu mixes lumière et tension.")

    if bpms:
        med = float(np.median(bpms))
        if med < 95:
            insights.append(f"Tempo médian ~{med:.0f} BPM : beaucoup de ballades / midtempo posé.")
        elif med > 120:
            insights.append(f"Tempo médian ~{med:.0f} BPM : profil plutôt dance / énergie.")
        else:
            insights.append(f"Tempo médian ~{med:.0f} BPM : zone pop / groove confortable.")

    if top_keys:
        insights.append(
            "Tonalités fréquentes (échantillon) : "
            + ", ".join(f"{k} ({c})" for k, c in top_keys[:5])
            + "."
        )
        # Relative / parallel hints
        roots = Counter(k.split()[0] for k, _ in top_keys)
        if roots:
            insights.append(
                f"Centres tonals récurrents : {', '.join(n for n,_ in roots.most_common(4))} "
                "(utile pour improviser dans ces familles d'accords)."
            )

    if top_genres:
        insights.append(
            "Styles détectés dans les titres : "
            + ", ".join(f"{n}" for n, _ in top_genres[:5])
            + "."
        )

    insights.append(
        "Pour les progressions d'accords exactes (I–V–vi–IV, ii–V–I…), "
        "un outil dédié type Chordify / Mixed In Key / Cyanite est plus précis que l'estimation chroma seule."
    )
    profile["insights"] = insights

    OUT.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    for line in insights:
        print("-", line)


if __name__ == "__main__":
    main()
