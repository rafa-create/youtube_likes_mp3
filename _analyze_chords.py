"""Chord / tempo / language analysis for creation targeting (full filtered playlist)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from collections import Counter, defaultdict
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
    r"greatest\s*hits|bandas\s*sonoras|official\s*trailer|"
    r"audition|game\s*highlights)",
    re.I,
)

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ROMAN_MAJ = ["I", "bII", "II", "bIII", "III", "IV", "bV", "V", "bVI", "VI", "bVII", "VII"]
ROMAN_MIN = ["i", "bii", "ii", "biii", "III", "iv", "bv", "v", "bVI", "VI", "bVII", "vii"]

FR_HINTS = re.compile(
    r"\b(le|la|les|des|une|aux|pour|dans|avec|sans|mon|ton|son|notre|"
    r"pomme|louane|angele|bigflo|ninho|stromae|mika|coeur|amour|vie|"
    r"paroles|clip\s*officiel|francais|français)\b|"
    r"[àâäéèêëïîôùûç]",
    re.I,
)
ES_HINTS = re.compile(
    r"\b(el|la|los|las|una|para|con|amor|corazon|español|espanol|"
    r"reggaeton|bachata|despeinada|official\s*video\s*español)\b|"
    r"[ñ¿¡]",
    re.I,
)
EN_HINTS = re.compile(
    r"\b(the|and|you|love|heart|night|official|lyrics|feat|featuring|"
    r"remix|acoustic|cover|music\s*video)\b",
    re.I,
)
INSTR_HINTS = re.compile(
    r"\b(instrumental|piano|orchestr|soundtrack|no\s*lyrics|karaoke)\b",
    re.I,
)


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


def detect_language(title: str) -> str:
    if INSTR_HINTS.search(title):
        return "instrumental"
    fr = len(FR_HINTS.findall(title))
    es = len(ES_HINTS.findall(title))
    en = len(EN_HINTS.findall(title))
    # accented FR chars boost
    if fr >= es and fr >= en and fr > 0:
        return "fr"
    if es > fr and es >= en:
        return "es"
    if en > 0:
        return "en"
    return "inconnu"


def bpm_bucket(bpm: float) -> str:
    if bpm < 80:
        return "<80 ballade"
    if bpm < 100:
        return "80–100 mid lent"
    if bpm < 120:
        return "100–120 pop"
    if bpm < 140:
        return "120–140 groove/dance"
    return "140+ rapide"


def select_tracks(limit: int = 0) -> list[Path]:
    files = sorted(MP3_DIR.glob("*.mp3"))
    kept = [f for f in files if not EXCLUDE.search(f.stem)]
    if limit and limit > 0 and len(kept) > limit:
        step = max(1, len(kept) // limit)
        return kept[::step][:limit]
    return kept


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
    if qual == "min":
        return ROMAN_MIN[deg]
    return ROMAN_MAJ[deg]


def pretty_chord(chord: str) -> str:
    name, qual = chord.split(":")
    return name if qual == "maj" else f"{name}m"


def smooth_labels(labels: list[int], min_run: int = 3) -> list[int]:
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


def extract_progressions(seq: list[str], n: int = 4) -> list[str]:
    collapsed = []
    for r in seq:
        if not collapsed or collapsed[-1] != r:
            collapsed.append(r)
    return ["-".join(collapsed[i : i + n]) for i in range(len(collapsed) - n + 1)]


def analyze_chords(path: str, duration: float = 60.0) -> dict:
    import librosa

    p = Path(path)
    try:
        y, sr = librosa.load(str(p), sr=22050, mono=True, duration=duration)
        if len(y) < sr * 8:
            return {"file": p.name, "error": "too_short"}

        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if isinstance(tempo, np.ndarray):
            tempo = float(tempo[0]) if tempo.size else 0.0
        else:
            tempo = float(tempo)

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=2048)
        norms = np.linalg.norm(chroma, axis=0, keepdims=True) + 1e-9
        scores = CHORD_TEMPLATES @ (chroma / norms)
        labels = smooth_labels(scores.argmax(axis=0).tolist(), min_run=3)

        key_root, key_mode = estimate_key_from_chroma(chroma.mean(axis=1))
        key_name = f"{NOTES[key_root]} {'major' if key_mode == 'maj' else 'minor'}"

        chord_seq = [CHORD_NAMES[i] for i in labels]
        step = max(1, int(1.2 / (2048 / sr)))
        chord_ds = [chord_seq[i] for i in range(0, len(chord_seq), step)]
        absolutes = [pretty_chord(c) for c in chord_ds]
        romans = [to_roman(c, key_root, key_mode) for c in chord_ds]

        grams_roman = extract_progressions(romans, n=4)
        grams_abs = extract_progressions(absolutes, n=4)
        abs_top = Counter(grams_abs).most_common(3)
        roman_top = Counter(grams_roman).most_common(3)
        main_loop = abs_top[0][0] if abs_top else "-".join(
            [a for i, a in enumerate(absolutes) if i == 0 or a != absolutes[i - 1]][:6]
        )

        part = np.partition(scores, -2, axis=0)
        margin = float(np.mean(part[-1] - part[-2]))
        lang = detect_language(p.stem)

        return {
            "file": p.name,
            "key": key_name,
            "bpm": round(tempo, 1),
            "bpm_bucket": bpm_bucket(tempo),
            "language": lang,
            "main_loop": main_loop,
            "progression_top": roman_top,
            "absolute_top": abs_top,
            "chord_counts": Counter(absolutes).most_common(8),
            "confidence": round(margin, 4),
            "grams": grams_roman,
            "grams_abs": grams_abs,
        }
    except Exception as exc:
        return {"file": p.name, "error": str(exc)}


def _job(args: tuple[str, float]) -> dict:
    return analyze_chords(*args)


def build_creation_recipes(ok: list[dict], top_loops: list[tuple[str, int]], n: int = 8) -> list[dict]:
    recipes = []
    for loop, count in top_loops[:n]:
        tracks = [r for r in ok if loop in (r.get("grams_abs") or []) or r.get("main_loop") == loop]
        if not tracks:
            tracks = [r for r in ok if any(loop == g for g, _ in (r.get("absolute_top") or []))]
        if not tracks:
            continue
        bpms = [r["bpm"] for r in tracks if r.get("bpm")]
        langs = Counter(r.get("language", "inconnu") for r in tracks)
        keys = Counter(r.get("key", "?") for r in tracks)
        buckets = Counter(r.get("bpm_bucket", "?") for r in tracks)
        romans = Counter()
        for r in tracks:
            for g, c in r.get("progression_top") or []:
                romans[g] += c
        recipes.append(
            {
                "chords": loop,
                "degrees": romans.most_common(1)[0][0] if romans else None,
                "count": count,
                "tracks": len(tracks),
                "bpm_mean": round(float(np.mean(bpms)), 1) if bpms else None,
                "bpm_median": round(float(np.median(bpms)), 1) if bpms else None,
                "tempo_bucket": buckets.most_common(1)[0][0] if buckets else None,
                "language": langs.most_common(1)[0][0] if langs else None,
                "languages": [{"name": k, "count": v} for k, v in langs.most_common()],
                "key": keys.most_common(1)[0][0] if keys else None,
                "examples": [t["file"] for t in tracks[:3]],
                "recipe": (
                    f"Écrire autour de {loop}"
                    + (f" (~{romans.most_common(1)[0][0]})" if romans else "")
                    + (f" · tempo ~{round(float(np.median(bpms)))} BPM" if bpms else "")
                    + (f" · langue {langs.most_common(1)[0][0]}" if langs else "")
                    + (f" · tonalité type {keys.most_common(1)[0][0]}" if keys else "")
                ),
            }
        )
    return recipes


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="0 = toute la playlist filtrée")
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    selected = select_tracks(args.limit)
    n_selected = len(selected)
    print(
        f"Chord+tempo+lang: {n_selected} tracks "
        f"(duration={args.duration}s, workers={args.workers})"
    )

    results = []
    jobs = [(str(t), args.duration) for t in selected]
    done = 0
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = [pool.submit(_job, j) for j in jobs]
        for fut in as_completed(futs):
            done += 1
            if done % 25 == 0 or done == len(futs):
                print(f"  progress {done}/{len(futs)}")
            results.append(fut.result())

    ok = [r for r in results if "error" not in r and r.get("grams_abs")]
    ok_conf = [r for r in ok if r.get("confidence", 0) >= 0.015] or ok

    prog_all = Counter()
    abs_all = Counter()
    chord_all = Counter()
    lang_all = Counter()
    tempo_all = Counter()
    for r in ok_conf:
        prog_all.update(r["grams"])
        abs_all.update(r.get("grams_abs") or [])
        chord_all.update(dict(r.get("chord_counts") or []))
        lang_all[r.get("language", "inconnu")] += 1
        tempo_all[r.get("bpm_bucket", "?")] += 1

    top_abs = abs_all.most_common(15)
    top_roman = prog_all.most_common(12)
    recipes = build_creation_recipes(ok_conf, top_abs, n=10)

    # Cross tabs: loop × language, loop × tempo for top loops
    cross_lang = []
    cross_tempo = []
    for loop, _ in top_abs[:6]:
        matching = [r for r in ok_conf if loop in (r.get("grams_abs") or [])]
        lc = Counter(r["language"] for r in matching)
        tc = Counter(r["bpm_bucket"] for r in matching)
        cross_lang.append({"chords": loop, "languages": [{"name": k, "count": v} for k, v in lc.most_common()]})
        cross_tempo.append({"chords": loop, "tempos": [{"name": k, "count": v} for k, v in tc.most_common()]})

    payload = {
        "method": "librosa chroma + BPM + langue titres (full filtered playlist)",
        "purpose": "creation_targeting",
        "tracks_considered": n_selected,
        "tracks_ok": len(ok_conf),
        "tracks_failed": len(results) - len(ok),
        "coverage_note": (
            f"Analyse création sur {len(ok_conf)}/{n_selected} pistes musicales filtrées "
            "(hors tutos/highlights/mix longs)."
        ),
        "languages": [{"name": k, "count": v} for k, v in lang_all.most_common()],
        "tempo_buckets": [{"name": k, "count": v} for k, v in tempo_all.most_common()],
        "top_chords": [{"name": n, "count": c} for n, c in chord_all.most_common(12)],
        "top_chord_loops": [{"name": g, "count": c} for g, c in top_abs],
        "top_progressions": [{"name": g, "count": c} for g, c in top_roman],
        "creation_recipes": recipes,
        "cross_language": cross_lang,
        "cross_tempo": cross_tempo,
        "examples": [
            {
                "progression": r.get("degrees"),
                "chords": r["chords"],
                "examples": r["examples"],
            }
            for r in recipes[:5]
        ],
        "sample_track_results": [
            {
                "file": r["file"],
                "key": r["key"],
                "bpm": r["bpm"],
                "language": r["language"],
                "chords": r.get("main_loop"),
                "confidence": r["confidence"],
                "top": [{"name": g, "count": c} for g, c in r["progression_top"]],
            }
            for r in sorted(ok_conf, key=lambda x: -x["confidence"])[:25]
        ],
    }

    profile = {}
    if PROFILE.is_file():
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    profile["chord_progressions"] = payload

    insights = [
        i
        for i in (profile.get("insights") or [])
        if "progression" not in i.casefold()
        and "boucle" not in i.casefold()
        and "degré" not in i.casefold()
        and "création" not in i.casefold()
        and "I–V" not in i
        and "accords" not in i.casefold()
    ]
    if recipes:
        top = recipes[0]
        insights.insert(
            0,
            f"Cible création #1 : {top['recipe']} (vu {top['count']}× / {top['tracks']} titres).",
        )
        insights.insert(
            1,
            "Top suites : "
            + ", ".join(f"{r['chords']} (~{r['bpm_median']} BPM, {r['language']})" for r in recipes[:4])
            + ".",
        )
    if lang_all:
        insights.append(
            "Langues détectées (titres) : "
            + ", ".join(f"{k} ({v})" for k, v in lang_all.most_common())
            + "."
        )
    profile["insights"] = insights

    PROFILE.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK={len(ok_conf)} failed={payload['tracks_failed']}")
    print("Creation recipes:")
    for r in recipes[:6]:
        print(f"  - {r['recipe']}")
    print(f"Wrote {PROFILE}")


if __name__ == "__main__":
    main()
