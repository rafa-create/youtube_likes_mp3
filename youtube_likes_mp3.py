import subprocess
import sys
import time
from pathlib import Path

# =========================
# CONFIGURATION
# =========================

OUTPUT_DIR = Path("mp3")
CHECK_EVERY = 300  # vérification toutes les 5 minutes

# Chrome = "chrome"
# Firefox = "firefox"
# Edge = "edge"
BROWSER = "chrome"

LIKED_PLAYLIST = "https://www.youtube.com/playlist?list=LL"

OUTPUT_DIR.mkdir(exist_ok=True)


def download_liked_videos():
    # Utilise le Python du venv (via -m) plutôt que yt-dlp du PATH système
    command = [
        sys.executable,
        "-m",
        "yt_dlp",

        # Récupère les cookies de ton navigateur
        "--cookies-from-browser", BROWSER,

        # Playlist "Vidéos J'aime"
        LIKED_PLAYLIST,

        # Audio uniquement
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "192K",

        # Ne retélécharge pas les fichiers déjà présents
        "--no-overwrites",

        # Nom du fichier
        "--output",
        str(OUTPUT_DIR / "%(title)s.%(ext)s"),

        # Continue même si une vidéo pose problème
        "--ignore-errors",

        # Évite de télécharger des miniatures/etc.
        "--no-write-thumbnail",
    ]

    print("\n🔎 Vérification de tes vidéos J'aime...")

    try:
        subprocess.run(command, check=False)
    except FileNotFoundError:
        print("❌ Python du venv ou le module yt-dlp est introuvable.")
        print(f"   Interpréteur : {sys.executable}")
        print("   Installe avec : .venv\\Scripts\\python.exe -m pip install yt-dlp")


def main():
    print("🎵 Téléchargeur automatique des vidéos J'aime")
    print(f"📁 Destination : {OUTPUT_DIR.absolute()}")
    print(f"⏱️ Vérification toutes les {CHECK_EVERY // 60} minutes")

    while True:
        download_liked_videos()

        print(
            f"\n💤 Attente de {CHECK_EVERY // 60} minutes "
            "avant la prochaine vérification..."
        )

        time.sleep(CHECK_EVERY)


if __name__ == "__main__":
    main()