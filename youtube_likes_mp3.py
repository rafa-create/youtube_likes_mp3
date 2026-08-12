import argparse
import sys
import time
from pathlib import Path

import yt_dlp

# =========================
# CONFIGURATION
# =========================

OUTPUT_DIR = Path("mp3")
COOKIES_FILE = Path("cookies.txt")
ARCHIVE_FILE = Path("downloaded.txt")  # IDs deja traites (plus fiable que --no-overwrites)
CHECK_EVERY = 300  # secondes

LIKED_PLAYLIST = "https://www.youtube.com/playlist?list=LL"

OUTPUT_DIR.mkdir(exist_ok=True)


def ydl_options() -> dict:
    if not COOKIES_FILE.is_file():
        raise FileNotFoundError(
            f"Fichier manquant : {COOKIES_FILE.resolve()}\n"
            "Sur Windows, Brave/Chrome/Edge ne marchent plus avec yt-dlp (DPAPI).\n"
            "1) Installe l'extension 'Get cookies.txt LOCALLY' dans Brave\n"
            "2) Sur youtube.com (connecte), exporte les cookies\n"
            "3) Place le fichier ici sous le nom cookies.txt"
        )

    return {
        "cookiefile": str(COOKIES_FILE),
        "paths": {"home": str(OUTPUT_DIR)},
        "outtmpl": {"default": "%(title)s.%(ext)s"},
        "format": "bestaudio/best",
        # YouTube exige un runtime JS pour resoudre les challenges (sinon seuls des images)
        "js_runtimes": {"node": {}},
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        # Archive : skip les videos deja telechargees meme si le titre change
        "download_archive": str(ARCHIVE_FILE),
        "ignoreerrors": True,
        "writethumbnail": False,
        "nooverwrites": True,
        "quiet": False,
        "no_warnings": False,
    }


def download_liked_videos() -> None:
    print("\nVerification de tes videos J'aime...")
    print(f"Cookies : {COOKIES_FILE.resolve()}")

    with yt_dlp.YoutubeDL(ydl_options()) as ydl:
        ydl.download([LIKED_PLAYLIST])


def main() -> None:
    # Evite UnicodeEncodeError sur les consoles Windows cp1252
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Telecharge tes videos YouTube J'aime en MP3")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Une seule passe puis quitte (sinon boucle toutes les 5 min)",
    )
    args = parser.parse_args()

    print("Telechargeur automatique des videos J'aime")
    print(f"Destination : {OUTPUT_DIR.resolve()}")
    if not args.once:
        print(f"Verification toutes les {CHECK_EVERY // 60} minutes")

    while True:
        try:
            download_liked_videos()
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
