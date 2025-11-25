#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import shlex
import re
from pathlib import Path
from datetime import datetime

# Optional banner display (like neofetch)
try:
    from pyfiglet import Figlet
    from termcolor import colored
except ImportError:
    Figlet = None
    colored = None


def validate_url(url):
    """Basic URL validation."""
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url_pattern.match(url) is not None


def validate_youtube_url(url):
    """Ensure URL is a valid YouTube link."""
    # Standard video IDs (11 chars)
    standard_pattern = re.compile(
        r'^https?://(www\.)?('
        r'youtube\.com/(watch\?v=|embed/|v/)|'
        r'music\.youtube\.com/watch\?v=|'
        r'youtu\.be/'
        r')([a-zA-Z0-9_-]{11})(&|#|/|\?|$)',
        re.IGNORECASE)

    # Playlists and other non-ID links
    no_id_pattern = re.compile(
        r'^https?://(www\.)?('
        r'youtube\.com/(attribution_link\?a=|playlist\?list=)|'
        r'music\.youtube\.com/playlist\?list='
        r')[a-zA-Z0-9_&=%-]*$',
        re.IGNORECASE)

    # Prevent command injection
    if '://' in url:
        for char in [';', '&&', '||', '|', '`', '$(', '>', '<', '>>']:
            if char in url.split('://', 1)[1]:
                return False

    return bool(standard_pattern.match(url) or no_id_pattern.match(url))


def sanitize_filename(filename):
    """Clean filename to be safe for filesystem."""
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = sanitized.replace('../', '').replace('..\\', '')
    return sanitized[:255]

def print_banner():
    """Display the UTOOB banner."""
    if Figlet:
        f = Figlet(font='slant')
        banner = f.renderText('UTOOB')
        if colored:
            print(colored(banner, 'red'))
            print(colored("    Smart YouTube Downloader", 'white'))
            return

    # Fallback skull banner
    skull = r"""
      _______
     /       \   _    _ _______ ____   ____  ____ 
    |  \   /  | | |  | |__   __/ __ \ / __ \|  _ \
    |    ^    | | |  | |  | | | |  | | |  | | |_) |
    |   ___   | | |__| |  | | | |__| | |__| |  _ < 
     \_______/   \____/   |_|  \____/ \____/| |_) |
                                            |____/ 
    """
    if colored:
        print(colored(skull, 'red', attrs=['bold']))
    else:
        print(skull)

# ========== GLOBAL INSTALLATION ==========
def install_globally():
    """Install script to ~/.local/bin."""
    local_bin = Path.home() / ".local" / "bin"
    local_bin.mkdir(parents=True, exist_ok=True)
    
    target = local_bin / "utoob"
    
    # Create a wrapper script
    wrapper_content = f"""#!/usr/bin/env python3
# Auto-generated wrapper for utoob
import sys
import subprocess
from pathlib import Path

SCRIPT_PATH = Path("{Path(__file__).resolve()}")
subprocess.run([sys.executable, str(SCRIPT_PATH)] + sys.argv[1:])
"""
    
    try:
        target.write_text(wrapper_content)
        target.chmod(0o755)  # Make executable
        
        print(f"✅ Installed globally to: {target}")
        print("💡 You can now run 'utoob' from anywhere!")
        
        # Check if ~/.local/bin is in PATH
        local_bin_str = str(local_bin)
        path_env = os.environ.get('PATH', '')
        if local_bin_str not in path_env:
            shell = os.environ.get('SHELL', '')
            if 'zsh' in shell:
                rc_file = '~/.zshrc'
            else:
                rc_file = '~/.bashrc'
            print(f"\n⚠️  Note: Add this to your {rc_file}:")
            print(f'    export PATH="$HOME/.local/bin:$PATH"')
            print("   Then run: source " + rc_file)
        
        return True
    except Exception as e:
        print(f"❌ Global installation failed: {e}")
        return False

# ========== SELF-INSTALLATION ==========
# On first run, organize the script into its own folder
SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
SCRIPT_NAME = SCRIPT_PATH.name
FIRST_RUN = False

if SCRIPT_DIR.name != "utoob":
    UTOOB_FOLDER = SCRIPT_DIR / "utoob"
    NEW_SCRIPT_PATH = UTOOB_FOLDER / SCRIPT_NAME
    if not UTOOB_FOLDER.exists():
        FIRST_RUN = True
        
        # Show banner first!
        print_banner()
        
        print("\n🎬 First run detected - Setting up utoob...")
        UTOOB_FOLDER.mkdir()
        shutil.move(str(SCRIPT_PATH), str(NEW_SCRIPT_PATH))
        print(f"✓ Created folder: {UTOOB_FOLDER}")
        print(f"✓ Moved script to: {NEW_SCRIPT_PATH}")
        
        # Ask about global installation
        print("\n" + "="*50)
        response = input("📍 Install globally? (Run 'utoob' from anywhere) [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            # Need to restart first, then install globally
            print("\n🔄 Restarting to complete setup...\n")
            os.execv(sys.executable, [sys.executable, str(NEW_SCRIPT_PATH), "--install-global"] + sys.argv[1:])
        else:
            print("\n🔄 Restarting from new location...\n")
            os.execv(sys.executable, [sys.executable, str(NEW_SCRIPT_PATH)] + sys.argv[1:])
        sys.exit(0)

# Handle --install-global flag
if len(sys.argv) > 1 and sys.argv[1] == "--install-global":
    install_globally()
    sys.argv.pop(1)  # Remove the flag

# Now we're in the correct location
SCRIPT_DIR = Path(__file__).parent.resolve()
# System files are stored in a dedicated subfolder
SYS_FILES_DIR = SCRIPT_DIR / "sys_files"
SYS_FILES_DIR.mkdir(exist_ok=True)
CONFIG_FILE = SYS_FILES_DIR / "config.json"
CACHE_DIR = SYS_FILES_DIR / "cache"
DB_FILE = SYS_FILES_DIR / "history.db"
CACHE_DIR.mkdir(exist_ok=True)

# ========== DATABASE & CONFIG ==========
import sqlite3
import json
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, APIC

def init_database():
    """Setup SQLite history."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            download_date TEXT,
            file_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def check_history(url):
    """Check if URL is in history."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT title, download_date FROM history WHERE url = ?', (url,))
    result = cursor.fetchone()
    conn.close()
    return result

def add_to_history(url, title, file_path):
    """Log download to DB."""
    from datetime import datetime
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO history (url, title, download_date, file_path) VALUES (?, ?, ?, ?)',
                      (url, title, datetime.now().isoformat(), file_path))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Already exists
    conn.close()

def load_config():
    """Read config.json."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"download_path": "downloads"}

def save_config(config):
    """Write config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def fetch_musicbrainz_art(artist, album):
    """Get album art from MusicBrainz API."""
    try:
        # Search for release
        url = f"https://musicbrainz.org/ws/2/release/?query=artist:{artist}%20AND%20release:{album}&fmt=json"
        headers = {'User-Agent': 'utoob/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        
        if data.get('releases'):
            release_id = data['releases'][0]['id']
            # Get cover art
            art_url = f"https://coverartarchive.org/release/{release_id}/front"
            art_response = requests.get(art_url, timeout=5)
            if art_response.status_code == 200:
                return art_response.content
    except:
        pass
    return None

def add_metadata(file_path, title, artist="Unknown", album="YouTube", track_num=None, artwork=None):
    """Tag MP3 with ID3 metadata."""
    try:
        audio = MP3(file_path, ID3=ID3)
        
        # Add tags
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        audio.tags.add(TALB(encoding=3, text=album))
        
        if track_num:
            audio.tags.add(TRCK(encoding=3, text=str(track_num)))
        
        if artwork:
            audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=artwork))
        
        audio.save()
        return True
    except Exception as e:
        print(f"⚠️  Metadata tagging failed: {e}")
        return False

def is_playlist(url):
    """Check if URL is a playlist."""
    return 'playlist' in url or 'list=' in url

def get_yt_dlp_path():
    """Get path to yt-dlp binary, downloading if necessary."""
    # Check local cache first
    local_path = CACHE_DIR / "yt-dlp"
    if local_path.exists():
        return str(local_path)

    # Download if missing
    print("\n⬇️  yt-dlp not found in cache. Downloading latest version...")
    try:
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        local_path.chmod(0o755)  # Make executable
        print(f"✅ Installed yt-dlp to: {local_path}")
        return str(local_path)
    except Exception as e:
        print(f"❌ Failed to download yt-dlp: {e}")
        return None

def get_playlist_info(url):
    """Fetch playlist metadata via yt-dlp."""
    # Validate URL first
    if not validate_youtube_url(url):
        print("❌ Invalid YouTube URL format")
        return None, None

    yt_dlp_path = get_yt_dlp_path()
    if not yt_dlp_path:
        return None, None

    try:
        result = subprocess.run(
            [yt_dlp_path, '--flat-playlist', '--dump-json', url],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split('\n')
        if lines and lines[0].strip():
            parsed_data = json.loads(lines[0])
            playlist_title = parsed_data.get('playlist_title', 'Unknown Playlist')
            # Sanitize the playlist title to prevent path traversal
            sanitized_title = sanitize_filename(playlist_title)
            return len(lines), sanitized_title
        return None, None
    except (json.JSONDecodeError, subprocess.CalledProcessError, IndexError):
        return None, None

def download_media(url, is_audio=False):
    """Main download function."""
    # Validate URL first
    if not validate_youtube_url(url):
        print("❌ Invalid YouTube URL format")
        return

    config = load_config()
    # Downloads go inside the utoob folder
    download_path = SCRIPT_DIR / Path(config.get("download_path", "downloads"))

    # Check history
    history = check_history(url)
    if history:
        print(f"\n⚠️  This URL was already downloaded:")
        print(f"   Title: {history[0]}")
        print(f"   Date: {history[1][:10]}")
        response = input("\n   Download again anyway? [y/N]: ").strip().lower()
        if response not in ['y', 'yes']:
            print("   Skipped.")
            return

    # Check if playlist
    if is_playlist(url):
        count, playlist_name = get_playlist_info(url)
        if count:
            print(f"\n📋 Playlist Detected!")
            print(f"   Name: {playlist_name}")
            print(f"   Videos: {count}")
            print(f"   Location: downloads/Playlists/{playlist_name}/")
            response = input(f"\n   Download all {count} videos? [y/N]: ").strip().lower()
            if response not in ['y', 'yes']:
                print("   Cancelled.")
                return

            # Sanitize playlist name to prevent path traversal and other issues
            sanitized_playlist_name = sanitize_filename(playlist_name)

            # Create playlist folder
            playlist_folder = download_path / "Playlists" / sanitized_playlist_name
            playlist_folder.mkdir(parents=True, exist_ok=True)
            output_template = f"{playlist_folder}/%(playlist_index)s - %(title)s.%(ext)s"
            print(f"\n   ✓ Created folder: {playlist_folder.relative_to(SCRIPT_DIR)}")
        else:
            output_template = f"{download_path}/%(title)s.%(ext)s"
    else:
        download_path.mkdir(exist_ok=True, parents=True)
        output_template = f"{download_path}/%(title)s.%(ext)s"

    print(f"\n⬇️  Starting download...")

    yt_dlp_path = get_yt_dlp_path()
    if not yt_dlp_path:
        print("\n❌ Error: yt-dlp could not be found or installed.")
        return

    cmd = [yt_dlp_path, url, "-o", output_template]
    if is_audio:
        cmd.extend(["-x", "--audio-format", "mp3"])
        print("   Format: MP3 (audio only)")
    else:
        print("   Format: Best quality video")

    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Download complete!")
        print(f"   Saved to: {download_path.relative_to(SCRIPT_DIR)}/")

        # Add to history
        add_to_history(url, "Downloaded", str(download_path))

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Download failed")
        print(f"   Error: {e}")
        print("   Tip: Try updating yt-dlp with: pip install -U yt-dlp")

def batch_download():
    """Process multiple URLs."""
    print("\n📦 Batch Download Mode")
    print("   Paste multiple YouTube URLs, one per line")
    print("   Type 'done' when finished\n")

    urls = []
    while True:
        url = input(f"   URL #{len(urls)+1} (or 'done'): ").strip()
        if url.lower() == 'done':
            break
        if url:
            if not validate_youtube_url(url):
                print(f"   ❌ Invalid YouTube URL: {url}. Skipping...")
                continue
            urls.append(url)
            print(f"   ✓ Added ({len(urls)} total)")

    if not urls:
        print("\n   No URLs entered. Returning to menu...")
        return

    print(f"\n📋 Ready to process {len(urls)} URL(s)")
    is_audio = input("   Download as audio (MP3)? [y/N]: ").strip().lower() in ['y', 'yes']

    print(f"\n{'='*50}")
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing URL {i}...")
        download_media(url, is_audio=is_audio)
        if i < len(urls):
            print(f"\n{'='*50}")

    print(f"\n✅ Batch complete! Successfully processed {len(urls)} URL(s).")

def main_menu():
    while True:
        print("\n" + "="*50)
        print("           UTOOB DOWNLOADER MENU")
        print("="*50)
        print("  1. Download Video    - Best quality video")
        print("  2. Download Audio    - Extract MP3 audio")
        print("  3. Batch Download    - Multiple URLs at once")
        print("  4. Quit              - Exit program")
        print("="*50)

        choice = input("\nYour choice [1-4]: ").strip()

        if choice == '1':
            print("\n🎥 Video Download")
            url = input("   Paste YouTube URL: ").strip()
            if url:
                if not validate_youtube_url(url):
                    print("❌ Invalid YouTube URL format. Please enter a valid YouTube URL.")
                    continue
                download_media(url, is_audio=False)
            else:
                print("   No URL entered.")
        elif choice == '2':
            print("\n🎵 Audio Download")
            url = input("   Paste YouTube URL: ").strip()
            if url:
                if not validate_youtube_url(url):
                    print("❌ Invalid YouTube URL format. Please enter a valid YouTube URL.")
                    continue
                download_media(url, is_audio=True)
            else:
                print("   No URL entered.")
        elif choice == '3':
            batch_download()
        elif choice == '4':
            print("\n👋 Thanks for using utoob!")
            print("   Your downloads are in: utoob/downloads/\n")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, 3, or 4.")

def main():
    init_database()  # Initialize database on startup
    print_banner()
    main_menu()

if __name__ == "__main__":
    main()
