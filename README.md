<!-- README — guide de démarrage pour Rémy -->

<div align="center">

# 🎧 YouTube Likes → MP3

### Tes vidéos YouTube « J'aime », directement en MP3.

Un petit téléchargeur Python pour récupérer **tes vidéos aimées sur YouTube**, en extraire l'audio et les enregistrer dans un dossier local. Pas de site web, pas de compte à créer sur un service tiers : tout tourne **sur ton PC**.

**🪟 Windows** · **🐍 Python 3.12** · **💻 VS Code** · **🎵 MP3**

---

**Salut Rémy 👋** Ce guide est pour toi. Suis les étapes dans l'ordre : une fois la configuration faite, tu pourras relancer le programme en un clic.

[Installation](#-1--préparer-ton-pc) · [Cookies YouTube](#-3--récupérer-ton-fichier-cookiestxt) · [Lancement](#-4--lancer-le-téléchargement) · [Dépannage](#-en-cas-de-problème)

</div>

> [!IMPORTANT]
> Ce projet est prévu **pour Windows** : le lanceur `run.bat`, le chemin de Python et la détection de FFmpeg sont conçus pour cet environnement. Le programme télécharge les **vidéos que ton propre compte YouTube a aimées**, pas une playlist publique choisie à la main. N'utilise le téléchargement que pour les contenus dont tu as le droit de faire une copie.

## ✨ Ce que fait le programme

```text
Tes vidéos « J'aime » sur YouTube
                │
                ▼
       yt-dlp récupère l'audio
                │
                ▼
       FFmpeg convertit en MP3
                │
                ▼
          📁 mp3/
```

- Enregistre les fichiers dans le dossier **`mp3/`** du projet, en **MP3 à 192 kb/s** (qualité demandée au convertisseur, sans améliorer artificiellement la source).
- Garde la trace des vidéos déjà traitées dans **`downloaded.txt`**, pour éviter de tout retélécharger à chaque fois.
- Peut faire **un seul passage** ou revérifier tes « J'aime » **toutes les 5 minutes**.
- Le dossier `mp3/`, le fichier `cookies.txt` et l'archive `downloaded.txt` sont ignorés par Git : ils restent sur ton PC.

## 🧰 1 — Préparer ton PC

Installe ces quatre outils **avant** de lancer le script :

| Outil | À quoi il sert | Où le récupérer |
| :--- | :--- | :--- |
| **VS Code** | Ouvrir et lancer le projet | [code.visualstudio.com](https://code.visualstudio.com/) |
| **Python 3.12 (64 bits)** | Exécuter le programme | [python.org/downloads](https://www.python.org/downloads/) — choisis la version 3.12 pour Windows |
| **Node.js (LTS)** | Aider yt-dlp à résoudre les défis JavaScript de YouTube | [nodejs.org](https://nodejs.org/en/download) |
| **FFmpeg** | Convertir l'audio téléchargé en MP3 | Voir la commande ci-dessous |

**Pour Python :** installe la version **3.12**, puis vérifie qu'elle est accessible depuis un terminal. Si l'installateur propose d'ajouter Python au `PATH`, coche l'option. Dans VS Code, installe aussi l'extension **Python** publiée par Microsoft.

**Pour FFmpeg :** ouvre **PowerShell** (le terminal Windows) et lance :

```powershell
winget install --id Gyan.FFmpeg -e
```

Ferme puis rouvre VS Code après l'installation de Node.js et de FFmpeg, afin que leurs commandes soient disponibles dans les nouveaux terminaux.

Vérifie ensuite que les trois commandes répondent :

```powershell
py -3.12 --version
node --version
ffmpeg -version
```

> [!TIP]
> Si `ffmpeg` n'est pas reconnu immédiatement, le script sait également chercher l'installation **Gyan.FFmpeg** réalisée avec `winget`. Si Node.js ou Python n'est pas reconnu, rouvre le terminal et vérifie son installation.

## 📂 2 — Ouvrir le projet dans VS Code

### Télécharger le projet

Sur la [page du dépôt](https://github.com/rafa-create/youtube_likes_mp3), clique sur **Code → Download ZIP**, puis **extrais** le ZIP dans un dossier, par exemple `Documents\youtube_likes_mp3`.

Si Git est déjà installé, tu peux aussi utiliser :

```powershell
git clone https://github.com/rafa-create/youtube_likes_mp3.git
```

Dans VS Code : **Fichier → Ouvrir un dossier** et sélectionne le dossier du projet. Ouvre ensuite un terminal avec **Terminal → Nouveau terminal**. Toutes les commandes ci-dessous sont à exécuter **à la racine du projet** (là où se trouve `youtube_likes_mp3.py`).

### Créer ton Python isolé

Un *environnement virtuel* garde les dépendances du projet séparées du reste de ton PC :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip "yt-dlp[default]"
```

Le premier lancement installe `yt-dlp` **dans `.venv`**, sans modifier les autres projets Python de ton ordinateur.

Dans VS Code, fais **Ctrl + Maj + P → Python: Select Interpreter** et choisis :

```text
.venv\Scripts\python.exe
```

> [!NOTE]
> Le fichier `run.bat` et les configurations de lancement du dépôt cherchent **exactement** ce Python dans `.venv\Scripts\python.exe`. Il n'est pas nécessaire d'activer l'environnement manuellement.

## 🍪 3 — Récupérer ton fichier `cookies.txt`

Pour lire ta liste privée de vidéos « J'aime », le programme doit être connecté **à ton propre compte YouTube**. On utilise pour cela un **fichier texte exporté depuis ton navigateur**, pas un dossier à copier depuis Windows.

### Option recommandée : exporter uniquement les cookies YouTube

1. Dans **Chrome, Brave ou Edge**, installe l'extension **[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)**. Vérifie soigneusement son nom : **« LOCALLY »** fait partie du nom de l'extension recommandée.
2. Ouvre [youtube.com](https://www.youtube.com/) et connecte-toi au compte dont tu veux récupérer les vidéos « J'aime ».
3. Depuis un onglet **YouTube**, ouvre l'extension et choisis l'exportation des cookies **du site courant uniquement**, au format **Netscape / cookies.txt** (l'intitulé exact dépend de la version de l'extension). N'exporte pas les cookies de tous tes sites.
4. Dans les téléchargements de ton navigateur, récupère le fichier `.txt` exporté. Renomme-le **`cookies.txt`** — vérifie qu'il ne s'appelle pas `cookies.txt.txt`.
5. Place ce fichier **à la racine du projet**, juste à côté de `youtube_likes_mp3.py`.

Le dossier doit ressembler à ceci :

```text
youtube_likes_mp3/
├── .venv/
├── .vscode/
├── cookies.txt            ← à créer toi-même, sur ton PC
├── youtube_likes_mp3.py
├── run.bat
└── README.md
```

<details>
<summary><strong>🔄 Si les cookies expirent trop vite ou si YouTube refuse la connexion</strong></summary>

La documentation de `yt-dlp` décrit une méthode plus fiable pour exporter les cookies YouTube :

1. Ouvre **une seule fenêtre de navigation privée**, connecte-toi à YouTube et garde **un seul onglet** ouvert.
2. Dans **ce même onglet**, va sur `https://www.youtube.com/robots.txt`.
3. Exporte les cookies **de youtube.com** avec l'extension depuis cet onglet (il peut être nécessaire d'autoriser l'extension en navigation privée).
4. Ferme cette fenêtre privée et **ne la réutilise pas**. Place le nouveau fichier exporté sous le nom `cookies.txt` dans le projet.

Guide de référence : [yt-dlp — Exporting YouTube cookies](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies).

</details>

> [!CAUTION]
> **`cookies.txt` est aussi sensible qu'une session connectée.** Ne l'envoie **jamais** à un ami (même à Rafa 😉), ne le colle pas dans un message et ne le publie pas sur GitHub. Rémy doit exporter **ses propres cookies sur son PC**. Si le fichier a été partagé par erreur, déconnecte la session concernée depuis les paramètres de sécurité de ton compte et exporte un nouveau fichier. L'extension est un logiciel tiers : vérifie ses autorisations avant de l'installer.

## ▶️ 4 — Lancer le téléchargement

### Mode simple : double-clic

Dans l'explorateur Windows, ouvre le dossier du projet et **double-clique sur `run.bat`**.

Le script démarre, vérifie ta liste « J'aime », télécharge les nouveaux audios et recommence **toutes les 5 minutes**. Pour l'arrêter, ferme la fenêtre ou utilise **Ctrl + C** dans son terminal.

### Depuis le terminal de VS Code

**Un seul passage** — pratique pour vérifier que tout fonctionne :

```powershell
.\.venv\Scripts\python.exe youtube_likes_mp3.py --once
```

**Surveillance continue** — nouvelle vérification toutes les 5 minutes :

```powershell
.\.venv\Scripts\python.exe youtube_likes_mp3.py
```

Tu peux aussi ouvrir l'onglet **Exécuter et déboguer** dans VS Code et choisir **« YouTube Likes MP3 (une fois) »** ou **« YouTube Likes MP3 (boucle) »**.

> [!TIP]
> Les MP3 apparaissent progressivement dans **`mp3/`**. Le programme conserve un fichier `downloaded.txt` : ne le supprime pas si tu veux éviter de retélécharger les vidéos déjà traitées. Les vidéos supprimées, privées ou indisponibles peuvent être ignorées avec un message d'erreur.

## 🧯 En cas de problème

| Message / symptôme | À vérifier |
| :--- | :--- |
| `py -3.12` introuvable | Installe **Python 3.12 pour Windows** et rouvre VS Code. Vérifie avec `py -3.12 --version`. |
| `Python du venv introuvable` | Reviens à l'étape 2 : `py -3.12 -m venv .venv`. |
| `No module named yt_dlp` | Réinstalle-le avec `.\.venv\Scripts\python.exe -m pip install --upgrade "yt-dlp[default]"`. |
| `cookies.txt` manquant | Vérifie le **nom exact** et l'emplacement du fichier à côté du script. |
| Connexion YouTube refusée / cookies invalides | Exporte à nouveau les cookies **de ton propre compte** ; consulte la méthode de navigation privée ci-dessus. |
| `ffmpeg introuvable` | Installe-le avec `winget install --id Gyan.FFmpeg -e` et relance VS Code. |
| Erreur JavaScript / `node` introuvable | Installe **Node.js LTS**, rouvre VS Code puis teste `node --version`. |
| Une vidéo ne se télécharge pas | Elle peut être indisponible ou protégée. Tu peux mettre `yt-dlp` à jour avec la commande de l'étape 2. |

Si tu vois une erreur, regarde **les dernières lignes du terminal** : elles indiquent généralement si le problème vient des cookies, de Python, de FFmpeg ou d'une vidéo précise.

---

<div align="center">

**🎶 Bonne écoute, Rémy !**

*Fait pour que tes « J'aime » deviennent ta bibliothèque MP3 locale.*

</div>
