"""Pilot chord-progression analysis on ~100 filtered MP3s (librosa chroma templates)."""
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
PROFILE = ROOT / "music_profile.json"

EXCLUDE = re.compile(
    r"(tuto|tutorial|after\s*movie|teaser|highlight|nba|gala|campagne|"
    r"full\s*album|1\s*hour|4\s*hours|9\s*hours|playlist|mix\s*\(|"
    r"greatest\s*hits|bandas\s*sonoras|official\s*trailer)",
    re.I,
)

# 24 major/minor triad templates in chroma space
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ROMAN_MAJ = ["I", "bII", "II", "bIII", "III", "IV", "bV", "V", "bVI", "VI", "bVII", "VII"]
ROMAN_MIN = ["i", "bii", "ii", "biii", "III", "iv", "bv", "v", "bVI", "VI", "bVII", "vii"]


def _triad_template(root: int, quality: str) -> np.ndarray:
    t = np.zeros(12, dtype=float)
    third = 4 if quality == "maj" else 3
    t[root] = 1.0
    t[(root + third) % 12] = 0.8
    t[(root + 7) % 12] = 0.9
    return t / (t.sum() + 1e-9)


CHORD_NAMES = [f"{n}:{q}" for n in NOTES for q in ("maj", "min")]
CHORD_TEMPLATES = np.stack(
    [_triad_template(i, q) for i in range(12) for q in ("maj", "min")]
)


def select_tracks(limit: int = 100) -> list[Path]:
    files = sorted(MP3_DIR.glob("*.mp3"))
    kept = [f for f in files if not EXCLUDE.search(f.stem)]
    if len(kept) <= limit:
        return kept
    step = max(1, len(kept) // limit)
    return kept[::step][:limit]


def estimate_key_from_chroma(chroma_avg: np.ndarray) -> tuple[int, str]:
    major = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    best = (-1e9, 0, "maj")
    v = chroma_avg / (chroma_avg.sum() + 1e-9)
    for i in range(12):
        maj = float(np.corrcoef(v, np.roll(major, i))[0, 1])
        minr = float(np.corrcoef(v, np.roll(minor, i))[0, 1])
        if maj > best[0]:
            best = (maj, i, "maj")
        if minr > best[0]:
            best = (minr, i, "min")
    return best[1], best[2]


def to_roman(chord: str, key_root: int, key_mode: str) -> str:
    name, qual = chord.split(":")
    root = NOTES.index(name)
    deg = (root - key_root) % 12
    if key_mode == "maj":
        base = ROMAN_MAJ[deg]
        return base if qual == "maj" else base.lower() if base.isupper() else base
    # minor key: keep common pop notation
    if qual == "min":
        return ROMAN_MIN[deg] if ROMAN_MIN[deg].islower() or ROMAN_MIN[deg] in {"III", "VI", "bVI", "bVII"} else ROMAN_MIN[deg]
    return ROMAN_MAJ[deg]


def smooth_labels(labels: list[int], min_run: int = 4) -> list[int]:
    if not labels:
        return labels
    out = labels[:]
    i = 0
    while i < len(out):
        j = i
        while j < len(out) and out[j] == out[i]:
            j += 1
        if (j - i) < min_run and i > 0:
            for k in range(i, j):
                out[k] = out[i - 1]
        i = j
    return out


def pretty_chord(chord: str) -> str:
    """C:maj -> C, A:min -> Am"""
    name, qual = chord.split(":")
    return name if qual == "maj" else f"{name}m"


def extract_progressions(seq: list[str], n: int = 4) -> list[str]:
    collapsed = []
    for r in seq:
        if not collapsed or collapsed[-1] != r:
            collapsed.append(r)
    return ["-".join(collapsed[i : i + n]) for i in range(len(collapsed) - n + 1)]


def analyze_chords(path: str, duration: float = 90.0) -> dict:
    import librosa

    p = Path(path)
    try:
        y, sr = librosa.load(str(p), sr=22050, mono=True, duration=duration)
        if len(y) < sr * 8:
            return {"file": p.name, "error": "too_short"}

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=2048)
        norms = np.linalg.norm(chroma, axis=0, keepdims=True) + 1e-9
        cnorm = chroma / norms
        scores = CHORD_TEMPLATES @ cnorm
        labels = smooth_labels(scores.argmax(axis=0).tolist(), min_run=3)

        chroma_avg = chroma.mean(axis=1)
        key_root, key_mode = estimate_key_from_chroma(chroma_avg)
        key_name = f"{NOTES[key_root]} {'major' if key_mode == 'maj' else 'minor'}"

        chord_seq = [CHORD_NAMES[i] for i in labels]
        step = max(1, int(1.2 / (2048 / sr)))
        chord_ds = [chord_seq[i] for i in range(0, len(chord_seq), step)]
        absolutes = [pretty_chord(c) for c in chord_ds]
        romans = [to_roman(c, key_root, key_mode) for c in chord_ds]

        grams_roman = extract_progressions(romans, n=4)
        grams_abs = extract_progressions(absolutes, n=4)

        # most common loop in this track (absolute)
        abs_top = Counter(grams_abs).most_common(3)
        roman_top = Counter(grams_roman).most_common(3)
        chord_hist = Counter(absolutes)

        # representative loop: first occurrence of the top absolute gram, else first 8 unique-collapsed
        collapsed_abs = []
        for a in absolutes:
            if not collapsed_abs or collapsed_abs[-1] != a:
                collapsed_abs.append(a)
        main_loop = abs_top[0][0] if abs_top else "-".join(collapsed_abs[:6])

        part = np.partition(scores, -2, axis=0)
        margin = float(np.mean(part[-1] - part[-2]))

        return {
            "file": p.name,
            "key": key_name,
            "n_chords": len(set(absolutes)),
            "progression_top": roman_top,
            "absolute_top": abs_top,
            "chord_counts": chord_hist.most_common(8),
            "main_loop": main_loop,
            "confidence": round(margin, 4),
            "grams": grams_roman,
            "grams_abs": grams_abs,
        }
    except Exception as exc:
        return {"file": p.name, "error": str(exc)}


def _job(args: tuple[str, float]) -> dict:
    return analyze_chords(*args)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--duration", type=float, default=90.0)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    tracks = select_tracks(args.limit)
    print(f"Chord pilot: {len(tracks)} tracks, duration={args.duration}s, workers={args.workers}")

    results = []
    jobs = [(str(t), args.duration) for t in tracks]
    done = 0
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = [pool.submit(_job, j) for j in jobs]
        for fut in as_completed(futs):
            done += 1
            if done % 10 == 0 or done == len(futs):
                print(f"  progress {done}/{len(futs)}")
            results.append(fut.result())

    ok = [r for r in results if "error" not in r and r.get("grams")]
    ok_conf = [r for r in ok if r.get("confidence", 0) >= 0.02] or ok

    prog_all = Counter()
    abs_all = Counter()
    chord_all = Counter()
    for r in ok_conf:
        prog_all.update(r["grams"])
        abs_all.update(r.get("grams_abs") or [])
        chord_all.update(dict(r.get("chord_counts") or []))

    top = [{"name": g, "count": c} for g, c in prog_all.most_common(12)]
    top_abs = [{"name": g, "count": c} for g, c in abs_all.most_common(12)]
    top_chords = [{"name": g, "count": c} for g, c in chord_all.most_common(12)]

    examples = []
    for g, _ in prog_all.most_common(5):
        matches = [r for r in ok_conf if g in r["grams"]]
        files = [r["file"] for r in matches][:3]
        # most common absolute realization of this roman progression among matches
        abs_real = Counter()
        for r in matches:
            for ag, _ac in r.get("absolute_top") or []:
                # keep abs loops that appear in same track
                abs_real[ag] += 1
        realization = abs_real.most_common(1)[0][0] if abs_real else None
        # better: for tracks containing roman g, pick their main_loop if related
        loops = Counter(r.get("main_loop") for r in matches if r.get("main_loop"))
        if loops:
            realization = loops.most_common(1)[0][0]
        examples.append(
            {
                "progression": g,
                "chords": realization,
                "examples": files,
            }
        )

    payload = {
        "method": "librosa chroma triad templates → accords absolus + degrés romains (pilote)",
        "tracks_considered": len(tracks),
        "tracks_ok": len(ok_conf),
        "tracks_failed": len(results) - len(ok),
        "coverage_note": (
            f"Pilote sur {len(ok_conf)}/{len(tracks)} pistes filtrées "
            "(hors tutos/mix longs/highlights) — estimation bruitée."
        ),
        "top_chords": top_chords,
        "top_chord_loops": top_abs,
        "top_progressions": top,
        "examples": examples,
        "sample_track_results": [
            {
                "file": r["file"],
                "key": r["key"],
                "confidence": r["confidence"],
                "chords": r.get("main_loop"),
                "top_chords": [{"name": n, "count": c} for n, c in (r.get("chord_counts") or [])[:5]],
                "top": [{"name": g, "count": c} for g, c in r["progression_top"]],
            }
            for r in sorted(ok_conf, key=lambda x: -x["confidence"])[:20]
        ],
    }

    profile = {}
    if PROFILE.is_file():
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    profile["chord_progressions"] = payload
    insights = profile.get("insights") or []
    insights = [
        i
        for i in insights
        if "progression" not in i.casefold()
        and "I–V–vi–IV" not in i
        and "accords" not in i.casefold()
    ]
    if top_abs:
        insights.append(
            "Boucles d'accords fréquentes (pilote) : "
            + ", ".join(f"{t['name']} ({t['count']})" for t in top_abs[:4])
            + f" · n={payload['tracks_ok']}."
        )
    if top:
        insights.append(
            "Même chose en degrés : "
            + ", ".join(f"{t['name']} ({t['count']})" for t in top[:4])
            + "."
        )
    profile["insights"] = insights
    PROFILE.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK tracks={len(ok_conf)} failed={payload['tracks_failed']}")
    print("Top absolute loops:")
    for t in top_abs[:8]:
        print(f"  {t['name']}: {t['count']}")
    print("Top chords:")
    for t in top_chords[:8]:
        print(f"  {t['name']}: {t['count']}")
    print(f"Wrote {PROFILE}")


if __name__ == "__main__":
    main()
