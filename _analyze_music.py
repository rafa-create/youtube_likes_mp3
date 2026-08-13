"""Analyze liked music: meta patterns + audio key/BPM on all (or sampled) MP3s."""
from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
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

INSTRUMENT_RULES = [
    ("piano", ["piano", "einaudi", "gibran alcocer", "ludovico", "yiruma", "tony ann", "jacob", "pianoforte"]),
    ("voix / chant", ["cover vocal", "a cappella", "acapella", "singing", "voix", "vocal", "lyrics", "pomme", "sia", "adele", "lana del rey", "aurora", "imany"]),
    ("guitare", ["guitar", "guitare", "fingerstyle", "acoustic", "spanish guitar", "ukulele", "banjo"]),
    ("synth / prod. electro", ["alan walker", "remix", "edm", "synth", "electronic", "lost frequencies", "nightcore", "monstercat", "dubstep", "house"]),
    ("cordes (violon/cello/harpe)", ["violin", "violon", "cello", "violoncelle", "harp", "harpe", "orchestre", "orchestra", "strings"]),
    ("batterie / rythme", ["drums", "batterie", "percussion", "drum"]),
    ("vents", ["flute", "flûte", "saxophone", "sax", "trumpet", "trompette", "clarinet", "shepherd"]),
    ("ambiant / bowls", ["singing bowl", "tibetan", "417hz", "ambient pad", "meditation"]),
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


def guess_instruments(text: str) -> list[str]:
    low = text.casefold()
    hits = []
    for name, keys in INSTRUMENT_RULES:
        if any(k in low for k in keys):
            hits.append(name)
    return hits


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


def analyze_audio(path: str | Path, duration: float = 60.0) -> dict | None:
    import librosa

    path = Path(path)
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

        rms = float(np.mean(librosa.feature.rms(y=y)[0]))
        centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))
        # Normalize-ish features to 0..1 for mood axes
        energy = float(np.clip((rms - 0.02) / 0.18, 0, 1))
        brightness = float(np.clip((centroid - 800) / 3200, 0, 1))
        tempo_n = float(np.clip((tempo - 60) / 100, 0, 1))
        mode_n = 1.0 if mode == "major" else 0.25
        # valence ~ major + brightness + mid tempo; energy ~ loudness + tempo
        valence = float(np.clip(0.45 * mode_n + 0.30 * brightness + 0.25 * tempo_n, 0, 1))
        energy_score = float(np.clip(0.55 * energy + 0.45 * tempo_n, 0, 1))

        return {
            "file": path.name,
            "bpm": round(tempo, 1),
            "key": key,
            "mode": mode,
            "key_confidence": round(conf, 3),
            "energy": round(energy_score, 3),
            "valence": round(valence, 3),
            "rms": round(rms, 4),
            "brightness": round(brightness, 3),
        }
    except Exception as exc:
        return {"file": path.name, "error": str(exc)}


def _analyze_job(args: tuple[str, float]) -> dict | None:
    path, duration = args
    return analyze_audio(path, duration=duration)


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


def mood_label(energy: float, valence: float) -> str:
    if energy >= 0.6 and valence >= 0.55:
        return "uplift / dance"
    if energy >= 0.6 and valence < 0.55:
        return "électro-mélancolie"
    if energy < 0.45 and valence < 0.5:
        return "intime / sombre"
    if energy < 0.45 and valence >= 0.5:
        return "doux / lumineux"
    return "équilibré / mid"


def build_mood_and_clusters(audio_rows: list[dict], k: int = 4) -> tuple[dict, list[dict]]:
    """Simple mood aggregates + numpy k-means on [bpm_n, energy, valence]."""
    if not audio_rows:
        return {}, []

    energies = [r["energy"] for r in audio_rows if "energy" in r]
    valences = [r["valence"] for r in audio_rows if "valence" in r]
    mood_counts = Counter(
        mood_label(r.get("energy", 0.5), r.get("valence", 0.5)) for r in audio_rows
    )

    mood = {
        "energy_mean": round(float(np.mean(energies)), 3) if energies else None,
        "energy_median": round(float(np.median(energies)), 3) if energies else None,
        "valence_mean": round(float(np.mean(valences)), 3) if valences else None,
        "valence_median": round(float(np.median(valences)), 3) if valences else None,
        "quadrants": [{"name": n, "count": c} for n, c in mood_counts.most_common()],
        "method": "heuristique BPM + mode + RMS + spectral centroid",
    }

    # Features for clustering
    X = []
    for r in audio_rows:
        bpm_n = float(np.clip((r.get("bpm", 120) - 60) / 100, 0, 1))
        X.append([bpm_n, r.get("energy", 0.5), r.get("valence", 0.5)])
    X = np.asarray(X, dtype=float)
    k = min(k, len(X))
    if k < 2:
        return mood, []

    rng = np.random.default_rng(42)
    centroids = X[rng.choice(len(X), size=k, replace=False)]
    labels = np.zeros(len(X), dtype=int)
    for _ in range(25):
        dists = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
        labels = dists.argmin(axis=1)
        new_centroids = np.array(
            [
                X[labels == i].mean(axis=0) if np.any(labels == i) else centroids[i]
                for i in range(k)
            ]
        )
        if np.allclose(new_centroids, centroids):
            break
        centroids = new_centroids

    CLUSTER_NAMES = {
        "électro-mélancolie": "Électro mélancolique",
        "uplift / dance": "Uplift / dance",
        "intime / sombre": "Intime / sombre",
        "doux / lumineux": "Doux / lumineux",
        "équilibré / mid": "Équilibré midtempo",
    }

    clusters = []
    for i in range(k):
        members = [audio_rows[j] for j in range(len(audio_rows)) if labels[j] == i]
        if not members:
            continue
        e = float(np.mean([m["energy"] for m in members]))
        v = float(np.mean([m["valence"] for m in members]))
        bpm = float(np.mean([m["bpm"] for m in members]))
        minor_share = sum(1 for m in members if m.get("mode") == "minor") / len(members)
        label = mood_label(e, v)
        # representative tracks: closest to centroid
        idxs = [j for j in range(len(audio_rows)) if labels[j] == i]
        sub = X[idxs]
        c = centroids[i]
        order = np.argsort(((sub - c) ** 2).sum(axis=1))
        examples = [members[int(o)]["file"] for o in order[:4]]
        clusters.append(
            {
                "id": i,
                "name": CLUSTER_NAMES.get(label, label),
                "count": len(members),
                "share_pct": round(100 * len(members) / len(audio_rows), 1),
                "bpm_mean": round(bpm, 1),
                "energy_mean": round(e, 3),
                "valence_mean": round(v, 3),
                "minor_pct": round(100 * minor_share, 1),
                "examples": examples,
            }
        )

    clusters.sort(key=lambda c: c["count"], reverse=True)
    return mood, clusters


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Profil musical likes YouTube")
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="Nombre max de MP3 audio à analyser (0 = tous)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=60.0,
        help="Secondes d'audio analysées par piste",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Workers parallèles pour l'analyse audio",
    )
    args = parser.parse_args()

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
    instruments: Counter[str] = Counter()
    instruments_untagged = 0
    for title in titles:
        artist, _ = split_artist_title(title)
        if artist:
            base = re.split(r"\s+(?:feat\.?|ft\.?|×|x)\s+", artist, flags=re.I)[0].strip()
            if len(base) > 1:
                artists[base] += 1
        for g in guess_genres(title):
            genres[g] += 1
        inst_hits = guess_instruments(title)
        if inst_hits:
            for inst in inst_hits:
                instruments[inst] += 1
        else:
            instruments_untagged += 1

    # --- Audio: all MP3s by default ---
    files = sorted(MP3_DIR.glob("*.mp3"))
    if args.sample and args.sample > 0 and len(files) > args.sample:
        step = max(1, len(files) // args.sample)
        sample = files[::step][: args.sample]
    else:
        sample = files

    print(
        f"Audio analysis: {len(sample)} / {len(files)} files "
        f"(duration={args.duration}s, workers={args.workers})"
    )
    audio_rows: list[dict] = []
    errors = 0
    jobs = [(str(f), args.duration) for f in sample]
    done = 0
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(_analyze_job, job) for job in jobs]
        for fut in as_completed(futures):
            done += 1
            if done % 25 == 0 or done == len(futures):
                print(f"  progress {done}/{len(futures)}")
            row = fut.result()
            if not row:
                errors += 1
                continue
            if "error" in row:
                errors += 1
                continue
            audio_rows.append(row)

    print(f"OK={len(audio_rows)} errors/skip={errors}")

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
    top_instruments = instruments.most_common()
    tagged_inst = sum(instruments.values()) or 1
    instruments_payload = [
        {
            "name": n,
            "count": c,
            "share_tagged_pct": round(100 * c / tagged_inst, 1),
        }
        for n, c in top_instruments
    ]
    preferred = instruments_payload[0] if instruments_payload else None

    mood, clusters = build_mood_and_clusters(audio_rows, k=4)

    # Sort sample tracks by "representativeness" = distance to global mean mood
    if audio_rows and "energy" in audio_rows[0]:
        ge = float(np.mean([r["energy"] for r in audio_rows]))
        gv = float(np.mean([r["valence"] for r in audio_rows]))
        scored = sorted(
            audio_rows,
            key=lambda r: (r.get("energy", 0.5) - ge) ** 2 + (r.get("valence", 0.5) - gv) ** 2,
        )
        sample_tracks = scored[:12]
    else:
        sample_tracks = audio_rows[:12]

    profile = {
        "playlist_count": len(titles),
        "mp3_count": len(files),
        "audio_sample_size": len(audio_rows),
        "audio_coverage_pct": round(100 * len(audio_rows) / max(1, len(files)), 1),
        "top_artists": [{"name": n, "count": c} for n, c in top_artists],
        "genre_signals": [{"name": n, "count": c} for n, c in top_genres],
        "instruments": instruments_payload,
        "instruments_untagged": instruments_untagged,
        "preferred_instrument": {
            "name": preferred["name"] if preferred else None,
            "count": preferred["count"] if preferred else 0,
            "share_tagged_pct": preferred["share_tagged_pct"] if preferred else 0,
            "method": "heuristique titres/artistes (pas classification audio timbre)",
        },
        "mood": mood,
        "clusters": clusters,
        "modes": [{"name": n, "count": c} for n, c in mode_counts.most_common()],
        "keys": [{"name": n, "count": c} for n, c in top_keys],
        "bpm_buckets": [{"name": n, "count": c} for n, c in bpm_counts.most_common()],
        "bpm_stats": {
            "mean": round(float(np.mean(bpms)), 1) if bpms else None,
            "median": round(float(np.median(bpms)), 1) if bpms else None,
            "p25": round(float(np.percentile(bpms, 25)), 1) if bpms else None,
            "p75": round(float(np.percentile(bpms, 75)), 1) if bpms else None,
        },
        "sample_tracks": sample_tracks,
        "insights": [],
    }

    insights = []
    insights.append(
        f"Couverture audio : {len(audio_rows)}/{len(files)} MP3 "
        f"({round(100 * len(audio_rows) / max(1, len(files)), 1)}%)."
    )
    if mood.get("quadrants"):
        top_q = mood["quadrants"][0]
        insights.append(
            f"Mood dominant : {top_q['name']} ({top_q['count']} pistes) · "
            f"énergie moy. {mood.get('energy_mean')} · valence moy. {mood.get('valence_mean')}."
        )
    if clusters:
        insights.append(
            "Clusters de goût : "
            + ", ".join(f"{c['name']} ({c['share_pct']}%)" for c in clusters[:4])
            + "."
        )
    if preferred:
        line = (
            f"Instrument préféré probable : {preferred['name']} "
            f"(~{preferred['share_tagged_pct']}% des titres taggés)."
        )
        if len(instruments_payload) > 1 and instruments_payload[1]["share_tagged_pct"] >= preferred["share_tagged_pct"] * 0.55:
            line += f" Secondaire fort : {instruments_payload[1]['name']}."
        insights.append(line)

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
            "Tonalités fréquentes : "
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
