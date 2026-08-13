"""Build liste_totale.md and echecs.md from playlist / archive / mp3 folder."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yt_dlp
from yt_dlp.utils import sanitize_filename

ROOT = Path(__file__).resolve().parent
PLAYLIST_TSV = ROOT / "_playlist.tsv"
ARCHIVE = ROOT / "downloaded.txt"
MP3_DIR = ROOT / "mp3"
OUT_TOTAL = ROOT / "liste_totale.md"
OUT_FAILED = ROOT / "echecs.md"
COOKIES = ROOT / "cookies.txt"
LIKED = "https://www.youtube.com/playlist?list=LL"


def export_playlist() -> list[tuple[str, str]]:
    if PLAYLIST_TSV.is_file() and PLAYLIST_TSV.stat().st_size > 1000:
        rows: list[tuple[str, str]] = []
        for line in PLAYLIST_TSV.read_text(encoding="utf-8").splitlines():
            if not line.strip() or "\t" not in line:
                continue
            vid, title = line.split("\t", 1)
            rows.append((vid.strip(), title.strip()))
        if len(rows) > 100:
            return rows

    opts = {
        "cookiefile": str(COOKIES),
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(LIKED, download=False)
    rows = []
    for e in info.get("entries") or []:
        if not e:
            continue
        vid = e.get("id") or ""
        title = e.get("title") or "(sans titre)"
        if vid:
            rows.append((vid, title))
    PLAYLIST_TSV.write_text(
        "\n".join(f"{vid}\t{title}" for vid, title in rows) + "\n",
        encoding="utf-8",
    )
    return rows


def load_archive() -> set[str]:
    ids: set[str] = set()
    if not ARCHIVE.is_file():
        return ids
    for line in ARCHIVE.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            ids.add(parts[1])
        elif parts:
            ids.add(parts[0])
    return ids


STOP = {
    "the", "and", "official", "video", "music", "audio", "lyrics", "lyric",
    "cover", "remix", "feat", "ft", "live", "full", "album", "song", "songs",
    "version", "clip", "visualizer", "hour", "hours", "best", "hits", "mix",
    "part", "sans", "titre", "officiel", "video", "oficial", "paroles",
}


def tokens(s: str) -> set[str]:
    s = sanitize_filename(s, restricted=False).casefold()
    s = re.sub(r"[^\wÀ-ÿ]+", " ", s, flags=re.UNICODE)
    parts = [p for p in s.split() if len(p) > 2 and p not in STOP]
    return set(parts)


def build_mp3_list() -> list[tuple[str, str, set[str]]]:
    """[(filename, stem, tokens)]"""
    out = []
    for p in MP3_DIR.glob("*.mp3"):
        out.append((p.name, p.stem, tokens(p.stem)))
    return out


def find_mp3(
    title: str,
    mp3s: list[tuple[str, str, set[str]]],
    *,
    allow_fuzzy: bool = True,
) -> str | None:
    # Exact / sanitized
    cands = {
        title,
        sanitize_filename(title, restricted=False),
        sanitize_filename(title, restricted=True),
        title.replace("/", "⧸").replace("|", "｜"),
    }
    stems = {stem.casefold(): name for name, stem, _ in mp3s}
    for c in cands:
        if c.casefold() in stems:
            return stems[c.casefold()]
        san = sanitize_filename(c, restricted=False).casefold()
        if san in stems:
            return stems[san]

    if not allow_fuzzy:
        return None

    tt = tokens(title)
    if len(tt) < 2:
        return None
    best_name = None
    best_score = 0.0
    for name, stem, mt in mp3s:
        if not mt:
            continue
        inter = tt & mt
        if len(inter) < 2:
            continue
        recall = len(inter) / len(tt)
        precision = len(inter) / len(mt)
        if recall < 0.6:
            continue
        score = 0.7 * recall + 0.3 * precision
        if len(inter) >= 3:
            score += 0.1
        # Short titles are collision-prone
        if len(tt) <= 2 and precision < 0.5:
            continue
        if score > best_score:
            best_score = score
            best_name = name
    if best_score >= 0.5:
        return best_name
    return None


def load_previous_reasons() -> dict[str, str]:
    path = OUT_FAILED
    if not path.is_file():
        return {}
    reasons: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| #"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 4:
            continue
        vid = parts[1].strip("` ")
        reason = parts[3]
        if vid and reason:
            reasons[vid] = reason
    return reasons


def probe_failure(vid: str) -> str:
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--cookies",
        str(COOKIES),
        "--js-runtimes",
        "node",
        "--skip-download",
        "-f",
        "bestaudio/best",
        f"https://www.youtube.com/watch?v={vid}",
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    err = ((proc.stderr or "") + "\n" + (proc.stdout or "")).strip()
    for line in err.splitlines():
        if line.startswith("ERROR:"):
            return re.sub(r"^ERROR:\s*(\[youtube\]\s*[^\s:]+:\s*)?", "", line).strip()
    if proc.returncode != 0:
        return err.splitlines()[-1] if err else f"exit {proc.returncode}"
    return "Accessible maintenant — MP3 manquant localement (à re-télécharger)"


def md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    playlist = export_playlist()
    archive = load_archive()
    mp3s = build_mp3_list()

    ok_rows = []
    fail_candidates = []  # (i, vid, title, reason_category)

    for i, (vid, title) in enumerate(playlist, start=1):
        in_arch = vid in archive
        # Fuzzy match only if archived (a download happened → file should exist)
        mp3 = find_mp3(title, mp3s, allow_fuzzy=in_arch)
        if mp3:
            ok_rows.append((i, vid, title, "OK", mp3))
        elif in_arch:
            fail_candidates.append((i, vid, title, "archive_sans_mp3"))
            ok_rows.append((i, vid, title, "ECHEC", "—"))
        else:
            fail_candidates.append((i, vid, title, "non_archive"))
            ok_rows.append((i, vid, title, "ECHEC", "—"))

    ok_count = sum(1 for r in ok_rows if r[3] == "OK")
    fail_count = len(ok_rows) - ok_count

    total_lines = [
        "# Liste totale — vidéos J'aime YouTube",
        "",
        f"- Playlist : **{len(playlist)}** entrées",
        f"- Archive yt-dlp (`downloaded.txt`) : **{len(archive)}** IDs",
        f"- Fichiers MP3 présents : **{len(mp3s)}**",
        f"- Matchés OK : **{ok_count}**",
        f"- Échecs / manquants : **{fail_count}**",
        "",
        "| # | Statut | ID | Titre | Fichier MP3 |",
        "|---:|:------:|:---|:------|:------------|",
    ]
    for i, vid, title, status, mp3 in ok_rows:
        total_lines.append(
            f"| {i} | {status} | `{vid}` | {md_escape(title)} | {('`' + md_escape(mp3) + '`') if mp3 != '—' else '—'} |"
        )
    total_lines += ["", f"**Résumé :** {ok_count} OK / {fail_count} échecs / {len(playlist)} total", ""]
    OUT_TOTAL.write_text("\n".join(total_lines), encoding="utf-8")
    print(f"Wrote {OUT_TOTAL.name}: {ok_count} OK, {fail_count} fail")

    fail_lines = [
        "# Échecs de téléchargement / conversion",
        "",
        f"Sur **{len(playlist)}** vidéos aimées, **{fail_count}** n'ont pas de MP3 correspondant localement.",
        "",
        "Sources : comparaison playlist ↔ dossier `mp3/` ↔ `downloaded.txt`, puis re-test yt-dlp pour la cause.",
        "",
        "| # | ID | Titre | Cause |",
        "|---:|:---|:------|:------|",
    ]

    prev_reasons = load_previous_reasons()

    for i, vid, title, cat in fail_candidates:
        safe = title.encode("ascii", "replace").decode("ascii")
        cached = prev_reasons.get(vid, "")
        cache_ok = bool(cached) and (
            "unavailable" in cached.casefold()
            or "downloaded.txt" in cached
            or "ffmpeg" in cached.casefold()
            or "Accessible" in cached
            or "Private" in cached
            or "manquant" in cached.casefold()
        )
        if cache_ok:
            reason = cached
            print(f"Reuse {vid} ({safe[:40]})")
        else:
            print(f"Probing {vid} ({safe[:50]})...")
            if cat == "archive_sans_mp3":
                reason = probe_failure(vid)
                if reason.startswith("Accessible") or "manquant localement" in reason:
                    reason = (
                        "Présent dans `downloaded.txt` mais fichier MP3 absent "
                        "(souvent échec ffmpeg au début du run, ou fichier depuis supprimé)"
                    )
                else:
                    reason = f"{reason} (ID encore dans l'archive locale)"
            else:
                reason = probe_failure(vid)
        fail_lines.append(f"| {i} | `{vid}` | {md_escape(title)} | {md_escape(reason)} |")

    fail_lines += [
        "",
        "## Notes",
        "",
        "- `Video unavailable` : privée, supprimée, ou restreinte.",
        "- Archive sans MP3 : yt-dlp a marqué l'ID comme fait, mais le `.mp3` n'est plus là (échec conversion ou suppression).",
        "- Lien : `https://www.youtube.com/watch?v=<ID>`",
        "",
    ]
    OUT_FAILED.write_text("\n".join(fail_lines), encoding="utf-8")
    print(f"Wrote {OUT_FAILED.name} ({len(fail_candidates)} rows)")


if __name__ == "__main__":
    main()
