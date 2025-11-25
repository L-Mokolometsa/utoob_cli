# 🎬 utoob – Smart YouTube Downloader

A lightweight, self‑installing CLI tool that downloads YouTube videos/audio, organizes them, and embeds proper metadata (track numbers, real album covers via MusicBrainz).

<div align="center">

[![Download utoob.py](https://img.shields.io/badge/⬇️_Download-utoob.py-blue?style=for-the-badge&logo=python)](https://raw.githubusercontent.com/YOUR_USERNAME/utoob/main/utoob.py)

</div>

---

## 📂 Folder Structure (after first run)
When you run `python3 utoob.py` for the first time, the script creates a single folder named **`utoob`** in the directory where you invoked it:
```
utoob/
├── utoob.py            # The script itself (moved here on first run)
├── downloads/          # Your downloaded music & videos
│   └── Playlists/      # Organized playlist downloads
└── sys_files/          # Internal files used by the program
    ├── config.json     # User preferences
    ├── cache/           # yt‑dlp binary and temporary files
    └── history.db       # SQLite DB tracking download history
```
All system‑related files are now isolated in `sys_files/`, keeping your `downloads/` folder clean.

---

## 🚀 Installation
1. **Clone the repository**:
```bash
git clone https://github.com/YOUR_USERNAME/utoob.git
cd utoob
```
2. **Install dependencies**:
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
pip install -r requirements.txt
```
3. **Run it** – the script will self-install into a `utoob/` folder:
```bash
python3 utoob.py
```
   *On first run, you'll be asked:*
   - ✅ **Install globally?** - Choose `y` to run `utoob` from anywhere, or `n` for local use only
   - The script will create the `utoob/` folder and set up `sys_files/`

---

## 🖥️ Platform Compatibility

| Platform | Core Features | Global Installation |
|----------|---------------|---------------------|
| **Linux** | ✅ Full support | ✅ Works (`~/.local/bin`) |
| **macOS** | ✅ Full support | ✅ Works (`~/.local/bin`) |
| **Termux** | ✅ Full support | ✅ Works (`~/.local/bin`) |
| **Windows** | ✅ Full support | ❌ Manual setup required |

### Windows Users
The script works on Windows, but global installation is not automatic. To use it:
```bash
cd path\to\utoob
python utoob.py
```
Or create a batch file manually in a directory that's in your PATH.

---

## 🎨 Visual Banner
On start you'll see a colorful banner:

![Main Menu](https://github.com/YOUR_USERNAME/utoob/releases/download/v1.0.0/utoob_menu.png)

If `pyfiglet` and `termcolor` are installed, the banner is rendered in a rainbow of colors.

---

## 📋 Usage
Run the script:
```bash
python3 utoob.py
```
You will see the interactive menu with 4 options:

**1. Download Video** - Download best quality video
**2. Download Audio** - Extract MP3 audio
**3. Batch Download** - Download multiple URLs at once
**4. Quit** - Exit the program

### Features
- **Playlist Detection**: Automatically detects playlists and asks before downloading all videos
- **Track Numbering**: Playlist items are numbered (e.g., `01 - Song Title.mp3`)
- **Download History**: Tracks downloaded URLs to avoid duplicates
- **Organized Storage**: Playlists saved in `downloads/Playlists/<PlaylistName>/`
- **Metadata Tagging**: Adds ID3 tags to audio files (title, artist, album, track number)
- **MusicBrainz Integration**: Fetches official album artwork when available

---

## 🗑️ Uninstall / Clean‑up
To completely remove utoob and all its data:
```bash
rm -rf /path/to/your/utoob   # removes script, downloads, and sys_files
```
If you only want to delete the program but keep your media, just delete the `utoob/` folder and keep the `downloads/` directory elsewhere.

---

## 📖 Further Reading
- **MusicBrainz API** – used for album‑cover lookup.
- **yt‑dlp** – automatically downloaded on first run and stored in `sys_files/cache/`.

Enjoy a tidy, intelligent YouTube downloader! 🎵
