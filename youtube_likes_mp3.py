import argparse
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import yt_dlp

# =========================
# CONFIGURATION
# =========================

OUTPUT_DIR = Path("mp3")
COOKIES_FILE = Path("cookies.txt")
ARCHIVE_FILE = Path("downloaded.txt")  # IDs deja traites, toutes playlists confondues
CHECK_EVERY = 300  # secondes

LIKED_PLAYLIST = "https://www.youtube.com/playlist?list=LL"

OUTPUT_DIR.mkdir(exist_ok=True)


def find_ffmpeg_dir() -> str | None:
    """Trouve le dossier contenant ffmpeg.exe (PATH ou install winget)."""
    from shutil import which

    found = which("ffmpeg")
    if found:
        return str(Path(found).parent)

    winget_root = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    if winget_root.is_dir():
        matches = sorted(winget_root.glob("Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe"))
        if matches:
            return str(matches[-1].parent)
    return None


def validate_playlist_url(url: str) -> str:
    """Accepte une URL YouTube de playlist ou de video contenant un parametre list=."""
    url = url.strip()
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise ValueError("URL de playlist invalide.") from exc

    allowed_hosts = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
    if (
        parsed.scheme not in {"https", "http"}
        or parsed.hostname not in allowed_hosts
        or parsed.path.rstrip("/") not in {"/playlist", "/watch"}
        or not any(value.strip() for value in parse_qs(parsed.query).get("list", []))
    ):
        raise ValueError(
            "Colle un lien de playlist YouTube valide, par exemple "
            "https://www.youtube.com/playlist?list=PL..."
        )
    return url


def ydl_options(*, require_cookies: bool) -> dict:
    if require_cookies and not COOKIES_FILE.is_file():
        raise FileNotFoundError(
            f"Fichier manquant : {COOKIES_FILE.resolve()}\n"
            "Pour telecharger tes videos J'aime, exporte les cookies de TON compte "
            "YouTube au format Netscape et place-les ici sous le nom cookies.txt.\n"
            "Consulte le README pour les instructions."
        )

    ffmpeg_dir = find_ffmpeg_dir()
    if not ffmpeg_dir:
        raise FileNotFoundError(
            "ffmpeg introuvable. Installe-le (ex: winget install Gyan.FFmpeg) "
            "puis relance VS Code pour rafraichir le PATH."
        )

    opts = {
        "paths": {"home": str(OUTPUT_DIR)},
        "outtmpl": {"default": "%(title)s.%(ext)s"},
        "format": "bestaudio/best",
        # YouTube peut exiger un runtime JS pour resoudre les challenges
        "js_runtimes": {"node": {}},
        "ffmpeg_location": ffmpeg_dir,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        # Une meme video n'est telechargee qu'une fois, meme si elle est dans
        # plusieurs playlists. Conserve downloaded.txt entre deux executions.
        "download_archive": str(ARCHIVE_FILE),
        "ignoreerrors": True,
        "writethumbnail": False,
        "nooverwrites": True,
        "quiet": False,
        "no_warnings": False,
    }
    # Les playlists publiques fonctionnent sans cookies. Si cookies.txt existe,
    # yt-dlp peut aussi acceder aux playlists privees autorisees pour ce compte.
    if COOKIES_FILE.is_file():
        opts["cookiefile"] = str(COOKIES_FILE)
    return opts


def download_playlist(url: str, *, liked: bool) -> None:
    opts = ydl_options(require_cookies=liked)
    print("\nVerification de tes videos J'aime..." if liked else "\nTelechargement de la playlist...")
    print(f"Source  : {url}")
    print(f"Cookies : {COOKIES_FILE.resolve() if 'cookiefile' in opts else 'non utilises (playlist publique)'}")
    print(f"FFmpeg  : {opts['ffmpeg_location']}")

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])


def main() -> None:
    # Evite UnicodeEncodeError sur les consoles Windows cp1252
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Telecharge tes videos YouTube J'aime ou une playlist YouTube en MP3."
    )
    parser.add_argument(
        "--playlist",
        nargs="?",
        const="",
        metavar="URL",
        help="URL d'une playlist YouTube ; sans URL, demande le lien dans le terminal.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Une seule passe puis quitte (sinon boucle toutes les 5 min).",
    )
    args = parser.parse_args()

    liked = args.playlist is None
    if liked:
        url = LIKED_PLAYLIST
    else:
        pasted_url = args.playlist.strip() or input("Colle l'URL de ta playlist YouTube : ").strip()
        try:
            url = validate_playlist_url(pasted_url)
        except ValueError as exc:
            parser.error(str(exc))

    print("Telechargeur YouTube -> MP3")
    print("Mode : videos J'aime" if liked else "Mode : playlist YouTube")
    print(f"Destination : {OUTPUT_DIR.resolve()}")
    if not args.once:
        print(f"Verification toutes les {CHECK_EVERY // 60} minutes")

    while True:
        try:
            download_playlist(url, liked=liked)
        except FileNotFoundError as exc:
            print(f"\n[ERREUR] {exc}")
            sys.exit(1)
        except yt_dlp.utils.DownloadError as exc:
            print(f"\n[ERREUR] yt-dlp : {exc}")

        if args.once:
            break

        print(
            f"\nAttente de {CHECK_EVERY // 60} minutes "
            "avant la prochaine verification..."
        )
        time.sleep(CHECK_EVERY)


if __name__ == "__main__":
    main()
