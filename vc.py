"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ᴠᴄ ꜱᴛʀᴇᴀᴍɪɴɢ ᴍᴏᴅᴜʟᴇ — ᴍᴀʀʀʏ ᴍᴜꜱɪᴄ ʙᴏᴛ
  Pyrogram + PyTgCalls 2.x
  Sources: YouTube · Spotify · SoundCloud · Any URL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import os
import re
import asyncio
import logging

import yt_dlp

logger = logging.getLogger(__name__)

API_ID   = int(os.environ.get("API_ID", "0") or "0")
API_HASH = os.environ.get("API_HASH", "")
SESSION  = os.environ.get("SESSION_SECRET", "")

_pyro  = None
_calls = None
_ready = False

CACHE_DIR = os.path.join(os.path.dirname(__file__), "saved")
os.makedirs(CACHE_DIR, exist_ok=True)

COOKIES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies.txt")


# ── Source detection ─────────────────────────────────────────────

_RE_YT      = re.compile(r"(youtube\.com|youtu\.be)", re.I)
_RE_SPOT    = re.compile(r"open\.spotify\.com", re.I)
_RE_SC      = re.compile(r"soundcloud\.com", re.I)
_RE_URL     = re.compile(r"^https?://")

def detect_source(query: str) -> str:
    """Return 'youtube' | 'spotify' | 'soundcloud' | 'url' | 'search'."""
    q = query.strip()
    if _RE_SPOT.search(q):   return "spotify"
    if _RE_YT.search(q):     return "youtube"
    if _RE_SC.search(q):     return "soundcloud"
    if _RE_URL.match(q):     return "url"
    return "search"


# ── Info extraction ──────────────────────────────────────────────

def _ytdl_opts_info():
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "default_search": "ytsearch",
        "noplaylist": True,
    }
    if os.path.exists(COOKIES):
        opts["cookiefile"] = COOKIES
    return opts


def extract_info(query: str) -> dict:
    """Return {id, title, duration, url, thumbnail} for any query/URL."""
    src = detect_source(query)

    if src == "spotify":
        return _extract_spotify(query)

    search = query if src in ("youtube", "soundcloud", "url") else f"ytsearch1:{query}"
    if src == "soundcloud":
        search = f"scsearch1:{query}"

    with yt_dlp.YoutubeDL(_ytdl_opts_info()) as ydl:
        info = ydl.extract_info(search, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return {
            "id":        info.get("id", ""),
            "title":     info.get("title", "Unknown"),
            "duration":  info.get("duration", 0),
            "url":       info.get("webpage_url") or info.get("url", query),
            "thumbnail": info.get("thumbnail", ""),
            "uploader":  info.get("uploader", ""),
        }


def _extract_spotify(url: str) -> dict:
    """Resolve Spotify URL → YouTube via yt-dlp spotify extractor or spotdl."""
    try:
        with yt_dlp.YoutubeDL(_ytdl_opts_info()) as ydl:
            info = ydl.extract_info(url, download=False)
            if info and "entries" in info:
                info = info["entries"][0]
            if info:
                return {
                    "id":        info.get("id", ""),
                    "title":     info.get("title", "Unknown"),
                    "duration":  info.get("duration", 0),
                    "url":       info.get("webpage_url") or info.get("url", url),
                    "thumbnail": info.get("thumbnail", ""),
                    "uploader":  info.get("uploader", ""),
                }
    except Exception as e:
        logger.warning(f"yt-dlp Spotify extract failed: {e}")

    try:
        from spotdl.utils.search import get_search_results
        from spotdl.utils.spotify import SpotifyClient
        SpotifyClient.init(
            client_id="5f573c9bc44c424699275c81a5d6e5d7",
            client_secret="212476d9b0f3472eaa762d90b19b0ba8",
        )
        results = get_search_results(url)
        if results:
            t = results[0]
            yt_url = f"https://www.youtube.com/watch?v={t.song_id}" if getattr(t, "song_id", None) else f"ytsearch1:{t.name} {' '.join(a.name for a in t.artists)}"
            return extract_info(yt_url)
    except Exception as e:
        logger.warning(f"spotdl Spotify extract failed: {e}")

    return {"id": "", "title": url, "duration": 0, "url": url, "thumbnail": "", "uploader": ""}


# ── Download ─────────────────────────────────────────────────────

def _audio_out(uid: str) -> str:
    return os.path.join(CACHE_DIR, f"vc_a_{uid}.mp3")

def _video_out(uid: str) -> str:
    return os.path.join(CACHE_DIR, f"vc_v_{uid}.mp4")


def _safe_uid(url_or_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", url_or_id)[:60]


async def download_audio(url: str, uid: str) -> str:
    """Download best-quality audio as 320kbps MP3. Returns path."""
    uid  = _safe_uid(uid or url)
    out  = _audio_out(uid)
    tmpl = os.path.join(CACHE_DIR, f"vc_a_{uid}.%(ext)s")

    if os.path.exists(out) and os.path.getsize(out) > 10_000:
        return out

    opts = {
        "format": "bestaudio/best",
        "outtmpl": tmpl,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    if os.path.exists(COOKIES):
        opts["cookiefile"] = COOKIES

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: _run_ydl(opts, url))

    if not os.path.exists(out) or os.path.getsize(out) < 1000:
        raise RuntimeError("Audio download failed or file is too small")
    return out


async def download_video(url: str, uid: str) -> str:
    """Download best video+audio (max 720p) as MP4. Returns path."""
    uid = _safe_uid(uid or url)
    out = _video_out(uid)
    tmpl = os.path.join(CACHE_DIR, f"vc_v_{uid}.%(ext)s")

    if os.path.exists(out) and os.path.getsize(out) > 10_000:
        return out

    opts = {
        "format": (
            "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]"
            "/bestvideo[height<=720]+bestaudio"
            "/best[height<=720]/best"
        ),
        "outtmpl": tmpl,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    if os.path.exists(COOKIES):
        opts["cookiefile"] = COOKIES

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: _run_ydl(opts, url))

    if not os.path.exists(out) or os.path.getsize(out) < 1000:
        raise RuntimeError("Video download failed or file is too small")
    return out


def _run_ydl(opts: dict, url: str):
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])


# ── PyTgCalls init ───────────────────────────────────────────────

async def init():
    """Init Pyrogram client + PyTgCalls. Call once at bot startup."""
    global _pyro, _calls, _ready
    if not SESSION:
        logger.warning("SESSION_SECRET not set — VC streaming disabled.")
        return
    if not API_ID or not API_HASH:
        logger.warning("API_ID / API_HASH missing — VC streaming disabled.")
        return
    try:
        from pyrogram import Client
        from pytgcalls import PyTgCalls

        _pyro = Client(
            "assistant_vc",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=SESSION,
            no_updates=True,
        )
        _calls = PyTgCalls(_pyro)
        await _pyro.start()
        await _calls.start()
        _ready = True
        logger.info("✅ PyTgCalls VC client ready!")
    except Exception as exc:
        logger.error(f"❌ VC init failed: {exc}")
        _ready = False


def is_ready() -> bool:
    return _ready


# ── Stream helpers ───────────────────────────────────────────────

async def play_audio(chat_id: int, file_path: str):
    """Join group VC and stream audio file."""
    from pytgcalls.types import MediaStream
    await _calls.play(chat_id, MediaStream(file_path))


async def play_video(chat_id: int, file_path: str):
    """Join group VC and stream video file (audio + video)."""
    from pytgcalls.types import MediaStream
    await _calls.play(chat_id, MediaStream(file_path))


async def leave(chat_id: int):
    """Leave the VC."""
    try:
        await _calls.leave_call(chat_id)
    except Exception:
        pass
