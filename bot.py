"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ᴍᴀʀʀʏ ᴍᴜꜱɪᴄ ʙᴏᴛ  —  ᴠ 9.5
  © 2026 ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, io, time, asyncio, logging, aiohttp, psutil
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes,
)
from YUKIYTAPI.database.marry import (
    get_spouse, is_married, marry, divorce,
    all_marriages, marriage_duration,
)
from YUKIYTAPI.database.members import add_member, get_members, member_count
import YUKIYTAPI.vc as vc

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN  = os.environ.get("BOT_TOKEN", "")
API_BASE   = "http://localhost:8000"
BOT_START  = time.time()
PFP_PATH   = os.path.join(os.path.dirname(__file__), "pfp.jpg")

# ── Owner & Logger ─────────────────────────────────────────────
OWNER_ID    = 6278373904
LOG_CHAT_ID = -1003986814657

# ── Version ───────────────────────────────────────────────────
BOT_VERSION   = "9.5"
LAST_UPDATED  = "14 June 2026"
PYTGCALLS_VER = "2.x"

# ── Font helper (screenshot style small-caps unicode) ─────────
_SC = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘQʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘQʀꜱᴛᴜᴠᴡxʏᴢ"
)

def sc(text: str) -> str:
    """Convert text to small-caps Unicode (screenshot style)."""
    return text.translate(_SC)


def btn(emoji: str, label: str) -> str:
    """ʹ Lᴀʙᴇʟ ˏ style button text."""
    return f"{emoji} ʹ {sc(label)} ˏ"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OWNER & LOGGER SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def log_event(bot, text: str):
    """Send a log message to LOG_CHAT_ID (silently ignores errors)."""
    try:
        await bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=apply_pe(text),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.warning(f"log_event failed: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PREMIUM CUSTOM EMOJI SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_PE: dict[str, str] = {
    "🎵": "5463107823946717464",   # NewsEmoji
    "🎶": "5219964773222864098",   # EffectEmoji
    "💍": "5262922516426420894",   # LoveDayEmoji
    "🌸": "5222044641200720562",   # EffectEmoji
    "🏓": "5269563867305879894",   # RestrictedEmoji
    "🌙": "5850203648558109348",   # DarkEmojis2
    "☀️": "5217464097234241939",   # EffectEmoji
    "❤️": "5852564725224706721",   # DarkEmojis2
    "💗": "5336791061949852403",   # MemeSetEmoji
    "💌": "5285184156555306745",   # LoveDayEmoji
    "💔": "5213157963023273778",   # EffectEmoji
    "👥": "5453957997418004470",   # GameEmoji
    "😔": "5343953693010044468",   # PeachCatEmoji
    "⏳": "5217697679030637222",   # EffectEmoji
    "🔍": "5231012545799666522",   # NewsEmoji
    "📋": "4954458300235121703",   # NewUsefulEmoji
    "🎀": "5375203677487248777",   # BirthdayCollection
    "🔊": "5980884380795539169",   # iconemoji1
    "👹": "5411360911208238991",   # PeachCatEmoji
    "🔑": "5278573677900752088",   # LoveDayEmoji
    "📤": "5445355530111437729",   # FinanceEmoji
    "✅": "5825480094520446830",   # SCAMIcon
    "❌": "5870706619838369648",   # DarkEmojis2
    "⚠️": "5206365592503722994",   # Icons_Anime
    "🌟": "5262485971655468699",   # StarEmoji
    "⭐": "5379668527919684482",   # AttractivePack
    "💫": "5220087815445959708",   # EffectEmoji
    "✨": "5217818964612108191",   # EffectEmoji
    "🔥": "5220166546491459639",   # EffectEmoji
    "💥": "5220229033970649796",   # EffectEmoji
    "🎊": "5201730588351945766",   # EffectEmoji
    "🎉": "5309827274445433091",   # AnimeEmojiPack
    "👑": "5433758796289685818",   # BirthdayCollection
    "💎": "5413887962591026442",   # CatPawsEmoji
    "🎧": "5341599033024586073",   # PeachCatEmoji
    "🎤": "5413567996117408386",   # CatPawsEmoji
    "🎼": "5866342164266486901",   # iconemoji1
    "🎮": "5316728625465146646",   # AdaptiveStatus
    "🌿": "5316784421385287192",   # AdaptiveStatus
    "🎯": "5350460637182993292",   # RestrictedEmoji
    "💬": "5316558016479245582",   # AdaptiveStatus
    "📱": "5292136849614055245",   # MyMelodyEmojiPack
    "🌍": "5399898266265475100",   # RestrictedEmoji
    "🏆": "5409008750893734809",   # RestrictedEmoji
    "🎸": "5316993667896981960",   # AdaptiveStatus
    "🐱": "5282816560128336499",   # RestrictedEmoji
    "🐾": "5316994101688677895",   # AdaptiveStatus
    "💐": "5190661263629243818",   # RestrictedEmoji
    "🦋": "5316790180936431490",   # AdaptiveStatus
    "👫": "5453957997418004470",   # GameEmoji (👥 substitute)
    "😋": "5343953693010044468",   # PeachCatEmoji substitute
    "🍛": "5375203677487248777",   # BirthdayCollection substitute
    "💪": "5251657358374886466",   # CatPawsEmoji
    "🫶": "5253576920993388584",   # CatPawsEmoji
    "😭": "5341472619252164000",   # PeachCatEmoji
    "😎": "5341509066344637610",   # PeachCatEmoji
    "🌺": "5222044641200720562",   # EffectEmoji (🌸 substitute)
    "😈": "5852519774096986622",   # DarkEmojis2
    "☠️": "5870511392099930851",   # DarkEmojis2
    "👁": "5870635761467920506",   # DarkEmojis2
    "📊": "5445355530111437729",   # FinanceEmoji substitute
}


def apply_pe(text: str) -> str:
    """Replace standard emojis with premium <tg-emoji> custom emoji tags."""
    for emoji, eid in _PE.items():
        if emoji in text:
            tag = f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>'
            text = text.replace(emoji, tag)
    return text


# ── System stats ──────────────────────────────────────────────
def get_uptime() -> str:
    elapsed = int(time.time() - BOT_START)
    h, r = divmod(elapsed, 3600)
    m, s = divmod(r, 60)
    return f"{h}h:{m:02}m:{s:02}s"


def get_system_stats() -> dict:
    disk   = psutil.disk_usage("/")
    cpu    = psutil.cpu_percent(interval=0.1)
    ram    = psutil.virtual_memory()
    return {
        "uptime":   get_uptime(),
        "storage":  round(disk.percent, 1),
        "cpu":      round(cpu, 1),
        "ram":      round(ram.percent, 1),
    }


# ── YouTube search ─────────────────────────────────────────────
async def search_youtube(query: str) -> list[dict]:
    import yt_dlp
    ydl_opts = {"quiet": True, "no_warnings": True,
                "extract_flat": True, "default_search": "ytsearch5"}
    loop = asyncio.get_event_loop()
    def _s():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            return info.get("entries", [])
    entries = await loop.run_in_executor(None, _s)
    out = []
    for e in entries[:5]:
        if e:
            out.append({"id": e.get("id",""), "title": e.get("title","?"),
                        "channel": e.get("uploader","?"), "duration": e.get("duration",0)})
    return out


def fmt_dur(s) -> str:
    try: s = int(s)
    except: return "?:??"
    m, s = divmod(s, 60); h, m = divmod(m, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


# ── Audio download via YUKI API ───────────────────────────────
async def download_audio(video_id: str) -> bytes | None:
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"{API_BASE}/download",
            params={"url": f"https://www.youtube.com/watch?v={video_id}", "type": "audio"},
            timeout=aiohttp.ClientTimeout(total=10)) as r:
            td = await r.json()
        token = td.get("download_token")
        if not token: return None
        async with sess.get(f"{API_BASE}/stream/{video_id}",
            params={"token": token, "type": "audio"},
            timeout=aiohttp.ClientTimeout(total=120)) as r:
            if r.status != 200: return None
            return await r.read()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# KEYBOARDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def home_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✦ ʹ 🎀 ᴀᴅᴅ ᴛᴏ ɢʀᴏᴜᴘ 🎀 ˏ ✦ ↗",
                              url="https://t.me/Urlord_musicbot?startgroup=true")],
        [InlineKeyboardButton("❦ ʹ 🪄 ᴄᴏᴍᴍᴀɴᴅꜱ ˏ ❦", callback_data="cmd:cmds_0"),
         InlineKeyboardButton("✿ ʹ 🔖 ᴠᴇʀꜱɪᴏɴ ˏ ✿",  callback_data="cmd:version")],
        [InlineKeyboardButton("꩜ ʹ 💍 ᴍᴀʀʀʏ ˏ ꩜ ↗",  url="https://t.me/Urlord_musicbot"),
         InlineKeyboardButton("꩜ ʹ 🌸 ᴄʜᴀᴛɪɴɢ ˏ ꩜ ↗", url="https://t.me/+9ViOjw22u6hiNWZl")],
        [InlineKeyboardButton("⟡ ʹ 🍬 ᴡᴇʙꜱɪᴛᴇ ˏ ⟡ ↗", url="https://t.me/ABOUTxYUTAA")],
        [InlineKeyboardButton("༒ ʹ 👑 ᴜʀʟᴏʀᴅ ˏ ༒ ↗",   url="https://t.me/zctol")],
    ])


# (emoji, display-label, callback-key, usage-hint)
CMDS_PAGES = [
    [
        ("🛡️","Admin",   "Admin",   "/ban /unban /kick /mute /unmute @user"),
        ("🔐","Auth",    "Auth",    "/auth @user — authorize a user"),
        ("📡","G-Cast",  "G-Cast",  "/broadcast [message] — send to all groups"),
        ("💬","Bl-Chat", "Bl-Chat", "/blacklist [word] — block words in chat"),
        ("👥","Bl-Users","Bl-Users","/blocklist — manage blocked users"),
        ("▶️","C-Play",  "C-Play",  "/cplay [link] — play from channel"),
        ("🚫","G-Ban",   "G-Ban",   "/gban @user — global ban"),
        ("🔁","Loop",    "Loop",    "/loop — toggle loop mode"),
        ("📋","Log",     "Log",     "/setlog [channel] — set log channel"),
        ("🏓","Ping",    "Ping",    "/ping — check bot speed & uptime"),
        ("🎵","Play",    "Play",    "/play [song name or YouTube link]"),
        ("🔀","Shuffle", "Shuffle", "/shuffle — shuffle the queue"),
        ("⏩","Seek",    "Seek",    "/seek [seconds] — jump to timestamp"),
        ("🎶","Song",    "Song",    "/song [name] — download song as file"),
        ("⚡","Speed",   "Speed",   "/speed [0.5-2.0] — change playback speed"),
    ],
    [
        ("🤝","Collab",   "Collab",   "/collab — collaboration system"),
        ("🏛️","Feds",    "Feds",     "/fed — federation ban system"),
        ("🧹","Clean",   "Clean",    "/clean — delete bot messages"),
        ("🤖","AI Tools","AI-Tools", "/ai [question] — ask AI assistant"),
        ("💰","Crypto",  "Crypto",   "/crypto [coin] — get crypto price"),
        ("📜","History", "History",  "/history — see recent play history"),
        ("🔕","DND",     "DND",      "/dnd — do not disturb mode"),
        ("👾","Clone",   "Clone",    "/clone — clone this bot"),
        ("🧵","String",  "String",   "/string — generate string session"),
        ("ℹ️","Info",    "Info",     "/info [@user] — get user info"),
    ],
    [
        ("💍","Marry",     "Marry",    "/marry @user — propose shaadi 💍"),
        ("💔","Divorce",   "Divorce",  "/divorce — talaq lo 💔"),
        ("💑","Spouse",    "Spouse",   "/spouse [@user] — apna saathi dekho"),
        ("👫","Marriages", "Marriages","/marriages — sab jodiyaan dekho"),
        ("🌅","Gud Mrng",  "Gud-Mrng", "/gm — Good Morning tag karo sab ko"),
        ("🌙","Gud Night", "Gud-Night","/gn — Good Night tag karo sab ko"),
        ("☀️","Afternoon", "Afternoon","/ga ya /afternoon — Good Afternoon"),
        ("🍽️","Lunch",    "Lunch",    "/lunch — Lunch time tag"),
        ("🌆","Dinner",    "Dinner",   "/dinner — Dinner time tag"),
        ("🎵","VC Play",   "VC-Play",  "/vcplay [gaana] — Voice Chat mein audio bajao"),
        ("📹","V Play",    "V-Play",   "/vplay [video name/URL] — VC mein video dikhao 720p"),
        ("⏹","VC Stop",   "VC-Stop",  "/vcstop — Voice Chat band karo"),
    ],
]


def cmds_keyboard(page: int):
    items = CMDS_PAGES[page]
    rows  = []
    for i in range(0, len(items), 3):
        row = [
            InlineKeyboardButton(
                f"✦ ʹ {c[0]} {sc(c[1])} ˏ ✦",
                callback_data=f"c:{c[2]}"
            )
            for c in items[i:i+3]
        ]
        rows.append(row)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("❮❮ ʙᴀᴄᴋ", callback_data=f"cmd:cmds_{page-1}"))
    nav.append(InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="cmd:home"))
    if page < len(CMDS_PAGES) - 1:
        nav.append(InlineKeyboardButton("ɴᴇxᴛ ❯❯", callback_data=f"cmd:cmds_{page+1}"))
    rows.append(nav)
    return InlineKeyboardMarkup(rows)


# Flat lookup: key → usage hint
_CMD_USAGE: dict[str, str] = {c[2]: c[3] for page in CMDS_PAGES for c in page}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MESSAGE TEMPLATES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def start_text(first_name: str) -> str:
    s = get_system_stats()
    return (
        f"✦ ❝ ᴍᴀʀʀʏ ᴍᴜꜱɪᴄ ʙᴏᴛ ❞ ✦\n\n"
        f"<blockquote>"
        f"⌯ ʜᴇʏ 💗 <b><i>{first_name}</i></b> — ᴡᴇʟᴄᴏᴍᴇ!\n"
        f"⌯ ɪ ᴀᴍ <b>ᴍᴀʀʀʏ</b> 🌸 <i>ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴍᴜꜱɪᴄ ᴄᴏᴍᴘᴀɴɪᴏɴ</i>\n\n"
        f"꩜ <b>ꜰᴇᴀᴛᴜʀᴇꜱ :</b>\n"
        f"  ✿ 🎵 ʏᴏᴜᴛᴜʙᴇ ꜱᴛʀᴇᴀᴍɪɴɢ &amp; ᴅᴏᴡɴʟᴏᴀᴅ\n"
        f"  ✿ 💍 ᴍᴀʀʀʏ / ᴅɪᴠᴏʀᴄᴇ ꜱʏꜱᴛᴇᴍ\n"
        f"  ✿ 🌅 ɢʀᴏᴜᴘ ɢʀᴇᴇᴛɪɴɢꜱ &amp; ᴛᴀɢɢɪɴɢ\n"
        f"  ✿ 🔊 ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜱᴜᴘᴘᴏʀᴛ\n\n"
        f"❧ <b>ꜱᴇʀᴠᴇʀ ꜱᴛᴀᴛꜱ :</b>\n"
        f"  🌸 ᴜᴘᴛɪᴍᴇ    » <code>{s['uptime']}</code>\n"
        f"  🌸 ꜱᴛᴏʀᴀɢᴇ  » <code>{s['storage']}%</code>\n"
        f"  🌸 ᴄᴘᴜ       » <code>{s['cpu']}%</code>\n"
        f"  🌸 ʀᴀᴍ       » <code>{s['ram']}%</code>"
        f"</blockquote>\n\n"
        f"<i>⟡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍᴀʀʀʏ ᴠ{BOT_VERSION} — ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ ⟡</i>"
    )


VERSION_TEXT = (
    f"✦ ❝ ᴍᴀʀʀʏ ᴠᴇʀꜱɪᴏɴ ɪɴꜰᴏ ❞ ✦\n\n"
    f"<blockquote>"
    f"⌯ <b>ʙᴏᴛ ɴᴀᴍᴇ  :</b> <code>ᴍᴀʀʀʏ ᴍᴜꜱɪᴄ ʙᴏᴛ</code>\n"
    f"⌯ <b>ᴠᴇʀꜱɪᴏɴ   :</b> <code>v{BOT_VERSION}</code>\n"
    f"⌯ <b>ᴜᴘᴅᴀᴛᴇᴅ  :</b> <code>{LAST_UPDATED}</code>\n"
    f"⌯ <b>ᴘʏᴛɢᴄᴀʟʟꜱ:</b> <code>{PYTGCALLS_VER}</code>\n\n"
    f"꩜ <b>ꜰᴇᴀᴛᴜʀᴇꜱ :</b>\n"
    f"  ✦ 🎵 ᴍᴜꜱɪᴄ ꜱᴛʀᴇᴀᴍɪɴɢ\n"
    f"  ✦ 💍 ᴍᴀʀʀʏ ꜱʏꜱᴛᴇᴍ\n"
    f"  ✦ 🌅 ɢʀᴏᴜᴘ ɢʀᴇᴇᴛɪɴɢꜱ\n"
    f"  ✦ 🔊 ᴠᴏɪᴄᴇ ᴄʜᴀᴛ"
    f"</blockquote>\n\n"
    f"<i>⟡ ᴅᴇᴠ: ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ ⟡</i>"
)

MAGIC_TEXT = (
    "✦ ❝ ᴍᴀɢɪᴄ ᴘᴀɴᴇʟ ❞ ✦\n\n"
    "<blockquote>"
    "⌯ <b>ᴄʜᴏᴏꜱᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ</b> 🎀\n"
    "⌯ <b>ᴀꜱᴋ ᴅᴏᴜʙᴛꜱ :</b> <a href='https://t.me/Zcziiyy'>ꜱᴜᴘᴘᴏʀᴛ ↗</a>\n\n"
    "✿ <i>ᴍᴜꜱɪᴄ • ᴍᴀʀʀʏ • ɢʀᴇᴇᴛɪɴɢꜱ • ᴠᴄ</i>"
    "</blockquote>\n\n"
    "<i>⟡ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ ꜱᴛᴀʀᴛ ᴡɪᴛʜ / ⟡</i>"
)

CMDS_HEADER = (
    "✦ ❝ ᴄᴏᴍᴍᴀɴᴅꜱ ᴍᴇɴᴜ ❞ ✦\n\n"
    "<blockquote>"
    "⌯ <b>ᴄʜᴏᴏꜱᴇ ᴀɴʏ ᴄᴀᴛᴇɢᴏʀʏ</b> 🪄\n"
    "⌯ <b>ꜱᴜᴘᴘᴏʀᴛ :</b> <a href='https://t.me/Zcziiyy'>ᴄʜᴀᴛ ↗</a>\n\n"
    "⌯ <i>ᴘᴀɢᴇ ɴᴀᴠɪɢᴀᴛᴇ ᴡɪᴛʜ ❯❯ ᴀɴᴅ ❮❮</i>"
    "</blockquote>"
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def _pfp_reply(message, caption: str, reply_markup=None):
    """Send pfp photo with caption + optional inline keyboard. Auto-applies premium emoji."""
    caption = apply_pe(caption)
    kwargs = dict(caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    try:
        with open(PFP_PATH, "rb") as f:
            await message.reply_photo(photo=f, **kwargs)
    except Exception:
        # Fallback to text if photo fails
        await message.reply_text(caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "User"
    chat = update.effective_chat
    await _pfp_reply(update.message, start_text(name), home_keyboard())
    # Log to group
    ulink = f"<a href='tg://user?id={user.id}'><b>{name}</b></a>"
    loc   = f"<code>{chat.title}</code> (<code>{chat.id}</code>)" if chat.type != "private" else "ᴅᴍ"
    await log_event(
        ctx.bot,
        f"<blockquote>"
        f"🌸 <b>ɴᴇᴡ ꜱᴛᴀʀᴛ</b>\n"
        f"👤 ᴜꜱᴇʀ: {ulink} (<code>{user.id}</code>)\n"
        f"📍 ᴄʜᴀᴛ: {loc}\n"
        f"🕐 {datetime.now().strftime('%d %b %Y %H:%M')}"
        f"</blockquote>",
    )


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _pfp_reply(update.message, MAGIC_TEXT, cmds_keyboard(0))


async def ping_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    s = get_system_stats()
    text = (
        f"✦ ❝ ᴘɪɴɢ ❞ ✦\n\n"
        f"<blockquote>"
        f"🏓 <b>ᴘᴏɴɢ!</b>\n\n"
        f"🌸 <b>ᴜᴘᴛɪᴍᴇ :</b> <code>{s['uptime']}</code>\n"
        f"🌸 <b>ᴄᴘᴜ    :</b> <code>{s['cpu']}%</code>\n"
        f"🌸 <b>ʀᴀᴍ    :</b> <code>{s['ram']}%</code>"
        f"</blockquote>"
    )
    await _pfp_reply(update.message, text)


async def stats_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    async with aiohttp.ClientSession() as sess:
        try:
            async with sess.get(f"{API_BASE}/stats",
                                timeout=aiohttp.ClientTimeout(total=5)) as r:
                d = await r.json()
            text = (
                "✦ ❝ ᴍᴀʀʀʏ ꜱᴛᴀᴛꜱ ❞ ✦\n\n"
                "<blockquote>"
                f"🎵 <b>ᴛᴏᴛᴀʟ ᴅᴏᴡɴʟᴏᴀᴅꜱ :</b> <code>{d.get('total_song_downloads',0)}</code>\n"
                f"💾 <b>ᴄᴀᴄʜᴇ ꜱɪᴢᴇ     :</b> <code>{d.get('total_cache_size_mb',0)} ᴍʙ</code>\n"
                f"🔑 <b>ᴀᴄᴛɪᴠᴇ ᴛᴏᴋᴇɴꜱ :</b> <code>{d.get('active_tokens',0)}</code>"
                "</blockquote>\n\n"
                "<i>⟡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍᴀʀʀʏ ʏᴛ ᴀᴘɪ ⟡</i>"
            )
        except Exception as e:
            text = f"❌ <code>{e}</code>"
    await _pfp_reply(update.message, text)


async def play_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = " ".join(ctx.args).strip() if ctx.args else ""
    if not q:
        return await update.message.reply_text(
            "❗ <b>ɢᴀᴀɴᴇ ᴋᴀ ɴᴀᴀᴍ ʟɪᴋʜᴏ!</b>\n\nExample: <code>/play Tum Hi Ho</code>",
            parse_mode=ParseMode.HTML)
    await _do_search(update.message, q, update.effective_chat.id)


async def song_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    url = " ".join(ctx.args).strip() if ctx.args else ""
    if not url or ("youtube" not in url and "youtu.be" not in url):
        return await update.message.reply_text(
            "❗ <b>YouTube URL ᴅᴀʟᴏ!</b>\n<code>/song https://youtube.com/watch?v=xxx</code>",
            parse_mode=ParseMode.HTML)
    if "v=" in url:
        vid = url.split("v=")[-1].split("&")[0]
    else:
        vid = url.split("youtu.be/")[-1].split("?")[0]
    await _download_and_send(update.message, vid, "Direct URL")


async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Track member for greetings
    if update.effective_user and update.effective_chat:
        u = update.effective_user
        add_member(update.effective_chat.id, u.id, u.first_name or "User", u.username or "")

    text = update.message.text.strip()
    if text.startswith("/"): return
    if "youtube.com" in text or "youtu.be" in text:
        vid = text.split("v=")[-1].split("&")[0] if "v=" in text else text.split("youtu.be/")[-1].split("?")[0]
        await _download_and_send(update.message, vid, "Direct URL")
    else:
        await _do_search(update.message, text, update.effective_chat.id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SEARCH & DOWNLOAD FLOW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def _do_search(message, query: str, chat_id: int):
    msg = await message.reply_text(
        f"<b>🔍 ꜱᴇᴀʀᴄʜɪɴɢ:</b> <i>{query}</i>\n<code>ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</code>",
        parse_mode=ParseMode.HTML)
    try:
        results = await search_youtube(query)
    except Exception as e:
        return await msg.edit_text(f"❌ <code>{e}</code>", parse_mode=ParseMode.HTML)

    if not results:
        return await msg.edit_text(
            "❌ <b>ᴋᴏɪ ɢᴀᴀɴᴀ ɴᴀʜɪ ᴍɪʟᴀ.</b>\n<i>ᴀʟᴀɢ ɴᴀᴀᴍ ᴛʀʏ ᴋᴀʀᴏ.</i>",
            parse_mode=ParseMode.HTML)

    keyboard = []
    for i, r in enumerate(results, 1):
        dur   = fmt_dur(r["duration"])
        title = r["title"][:42] + "…" if len(r["title"]) > 42 else r["title"]
        keyboard.append([InlineKeyboardButton(
            f"{i}. 🎵 {title} [{dur}]",
            callback_data=f"dl:{r['id']}:{r['title'][:28]}")])
    keyboard.append([
        InlineKeyboardButton("▶️ VC ᴍᴇ ʙᴀᴊᴀᴏ", callback_data=f"vc:search:{results[0]['id']}:{results[0]['title'][:28]}"),
        InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cmd:cancel"),
    ])

    await msg.edit_text(
        apply_pe(
            f"✦ ❝ ꜱᴇᴀʀᴄʜ ʀᴇꜱᴜʟᴛꜱ ❞ ✦\n\n"
            f"<blockquote>"
            f"🔍 <b>ǫᴜᴇʀʏ :</b> <i>{query}</i>\n"
            f"📋 <b>ꜰᴏᴜɴᴅ  :</b> {len(results)} ʀᴇꜱᴜʟᴛꜱ\n\n"
            f"⌯ <i>ᴀᴘɴᴀ ɢᴀᴀɴᴀ ᴄʜᴜɴᴏ 👇</i>"
            f"</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard))


async def _download_and_send(message, video_id: str, title: str):
    await message.chat.send_action(ChatAction.RECORD_VOICE)
    msg = await message.reply_text(
        apply_pe(
            f"✦ ❝ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ❞ ✦\n\n"
            f"<blockquote>"
            f"⏳ <b>ꜰᴇᴛᴄʜɪɴɢ ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ...</b>\n"
            f"🎵 <i>{title}</i>"
            f"</blockquote>"
        ),
        parse_mode=ParseMode.HTML)
    try:
        audio_bytes = await download_audio(video_id)
    except Exception as e:
        return await msg.edit_text(
            apply_pe(f"✦ ❝ ᴇʀʀᴏʀ ❞ ✦\n\n<blockquote>❌ <code>{e}</code></blockquote>"),
            parse_mode=ParseMode.HTML)

    if not audio_bytes:
        return await msg.edit_text(
            apply_pe(
                "✦ ❝ ꜰᴀɪʟᴇᴅ ❞ ✦\n\n"
                "<blockquote>❌ <b>ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ.</b>\n"
                "<i>ʏᴏᴜᴛᴜʙᴇ ɴᴇ ʙʟᴏᴄᴋ ᴋᴀʀ ᴅɪʏᴀ ʏᴀ ᴠɪᴅᴇᴏ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ ʜᴀɪ.</i></blockquote>"
            ),
            parse_mode=ParseMode.HTML)

    await msg.edit_text(
        apply_pe(
            f"✦ ❝ ꜱᴇɴᴅɪɴɢ ❞ ✦\n\n"
            f"<blockquote>📤 <b>ᴜᴘʟᴏᴀᴅɪɴɢ...</b>\n🎵 <i>{title}</i></blockquote>"
        ),
        parse_mode=ParseMode.HTML)
    await message.chat.send_action(ChatAction.UPLOAD_VOICE)

    af = io.BytesIO(audio_bytes)
    af.name = f"{video_id}.m4a"

    caption = apply_pe(
        f"✦ ❝ ᴍᴀʀʀʏ ᴍᴜꜱɪᴄ ❞ ✦\n\n"
        f"<blockquote>"
        f"🎶 <b>{title}</b>\n\n"
        f"<i>⋆｡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍᴀʀʀʏ ʏᴛ ᴀᴘɪ ｡⋆</i>\n"
        f"<i>© ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ</i>"
        f"</blockquote>"
    )
    kb = [[
        InlineKeyboardButton(btn("🎵","Aur Gaana"), switch_inline_query_current_chat="/play "),
        InlineKeyboardButton(btn("👨‍💻","Dev"), url="https://t.me/Zcziiyy"),
    ]]
    await message.reply_audio(audio=af, caption=caption,
                              parse_mode=ParseMode.HTML,
                              reply_markup=InlineKeyboardMarkup(kb))
    try: await msg.delete()
    except: pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VC SUPPORT (group voice chat)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VC_QUEUE: dict[int, list] = {}      # chat_id -> [items]
VC_ACTIVE: dict[int, str] = {}      # chat_id -> current title

# ── Pending marriage proposals (proposer_id -> target_id) ─────
PENDING_PROPOSALS: dict[int, int] = {}


def _source_emoji(src: str) -> str:
    return {"youtube": "▶️", "spotify": "🎧", "soundcloud": "🔊", "url": "🌐"}.get(src, "🎵")


async def _stream_audio_vc(chat_id: int, query: str, notify_msg):
    """Resolve query → download 320kbps audio → stream to VC."""
    if not vc.is_ready():
        await notify_msg.edit_text(
            apply_pe(
                "❌ <b>VC ᴄʟɪᴇɴᴛ ʀᴇᴀᴅʏ ɴᴀʜɪ ʜᴀɪ!</b>\n"
                "<blockquote>SESSION_SECRET ꜱᴇᴛ ᴋᴀʀᴏ ᴀᴜʀ ʙᴏᴛ ʀᴇꜱᴛᴀʀᴛ ᴋᴀʀᴏ.</blockquote>"
            ),
            parse_mode=ParseMode.HTML,
        )
        return

    src = vc.detect_source(query)
    ico = _source_emoji(src)

    await notify_msg.edit_text(
        apply_pe(
            f"<blockquote>{ico} <b>ꜱᴇᴀʀᴄʜɪɴɢ...</b> <i>{query}</i></blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, vc.extract_info, query)
    except Exception as e:
        return await notify_msg.edit_text(
            apply_pe(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>"), parse_mode=ParseMode.HTML
        )

    title = info.get("title", "Unknown")
    url   = info.get("url", query)
    uid   = info.get("id") or vc._safe_uid(url)
    dur   = info.get("duration", 0)
    dur_s = f"{dur // 60}:{dur % 60:02d}" if dur else "?"

    await notify_msg.edit_text(
        apply_pe(
            f"<blockquote>⬇️ <b>ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ 320ᴋʙᴘꜱ...</b>\n"
            f"{ico} <i>{title}</i>\n"
            f"⏱ {dur_s}</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )

    try:
        path = await vc.download_audio(url, uid)
    except Exception as e:
        return await notify_msg.edit_text(
            apply_pe(f"❌ <b>ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ:</b> <code>{e}</code>"),
            parse_mode=ParseMode.HTML,
        )

    await notify_msg.edit_text(
        apply_pe(
            f"<blockquote>▶️ <b>VC ᴍᴇ ʙᴀᴊ ʀᴀʜᴀ ʜᴀɪ!</b>\n"
            f"{ico} 🎵 <b>{title}</b>\n"
            f"⏱ {dur_s} • 🔊 320ᴋʙᴘꜱ\n\n"
            f"<i>⌯ /vcstop ꜱᴇ ʙᴀɴᴅ ᴋᴀʀᴏ</i></blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )

    try:
        await vc.play_audio(chat_id, path)
        VC_ACTIVE[chat_id] = title
    except Exception as e:
        await notify_msg.edit_text(
            apply_pe(f"❌ <b>VC ꜱᴛʀᴇᴀᴍ ᴇʀʀᴏʀ:</b> <code>{e}</code>"),
            parse_mode=ParseMode.HTML,
        )


async def _stream_video_vc(chat_id: int, query: str, notify_msg):
    """Resolve query → download 720p video → stream to VC."""
    if not vc.is_ready():
        await notify_msg.edit_text(
            apply_pe(
                "❌ <b>VC ᴄʟɪᴇɴᴛ ʀᴇᴀᴅʏ ɴᴀʜɪ ʜᴀɪ!</b>\n"
                "<blockquote>SESSION_SECRET ꜱᴇᴛ ᴋᴀʀᴏ ᴀᴜʀ ʙᴏᴛ ʀᴇꜱᴛᴀʀᴛ ᴋᴀʀᴏ.</blockquote>"
            ),
            parse_mode=ParseMode.HTML,
        )
        return

    src = vc.detect_source(query)
    ico = _source_emoji(src)

    await notify_msg.edit_text(
        apply_pe(
            f"<blockquote>{ico} <b>ᴠɪᴅᴇᴏ ꜱᴇᴀʀᴄʜɪɴɢ...</b> <i>{query}</i></blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, vc.extract_info, query)
    except Exception as e:
        return await notify_msg.edit_text(
            apply_pe(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>"), parse_mode=ParseMode.HTML
        )

    title = info.get("title", "Unknown")
    url   = info.get("url", query)
    uid   = info.get("id") or vc._safe_uid(url)
    dur   = info.get("duration", 0)
    dur_s = f"{dur // 60}:{dur % 60:02d}" if dur else "?"

    await notify_msg.edit_text(
        apply_pe(
            f"<blockquote>⬇️ <b>ᴠɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ (720ᴘ)...</b>\n"
            f"{ico} <i>{title}</i>\n"
            f"⏱ {dur_s}</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )

    try:
        path = await vc.download_video(url, uid)
    except Exception as e:
        return await notify_msg.edit_text(
            apply_pe(f"❌ <b>ᴠɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ:</b> <code>{e}</code>"),
            parse_mode=ParseMode.HTML,
        )

    await notify_msg.edit_text(
        apply_pe(
            f"<blockquote>📹 <b>VC ᴍᴇ ᴠɪᴅᴇᴏ ᴄʜᴀʟ ʀᴀʜᴀ ʜᴀɪ!</b>\n"
            f"{ico} 🎬 <b>{title}</b>\n"
            f"⏱ {dur_s} • 📺 720ᴘ ʜᴅ\n\n"
            f"<i>⌯ /vcstop ꜱᴇ ʙᴀɴᴅ ᴋᴀʀᴏ</i></blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )

    try:
        await vc.play_video(chat_id, path)
        VC_ACTIVE[chat_id] = title
    except Exception as e:
        await notify_msg.edit_text(
            apply_pe(f"❌ <b>VC ᴠɪᴅᴇᴏ ꜱᴛʀᴇᴀᴍ ᴇʀʀᴏʀ:</b> <code>{e}</code>"),
            parse_mode=ParseMode.HTML,
        )


async def vc_play_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle /vcplay — stream audio to group VC. Supports YT, Spotify, SoundCloud."""
    if update.effective_chat.type == "private":
        return await update.message.reply_text(
            apply_pe("❗ <b>VC ꜰᴇᴀᴛᴜʀᴇ ꜱɪʀꜰ ɢʀᴏᴜᴘ ᴍᴇ ᴋᴀᴀᴍ ᴋᴀʀᴛᴀ ʜᴀɪ!</b>"),
            parse_mode=ParseMode.HTML,
        )
    q = " ".join(ctx.args).strip() if ctx.args else ""
    if not q:
        return await update.message.reply_text(
            apply_pe(
                "<blockquote>❗ <b>ɢᴀᴀɴᴇ ᴋᴀ ɴᴀᴀᴍ ʟɪᴋʜᴏ!</b>\n"
                "<code>/vcplay Tum Hi Ho</code>\n"
                "<code>/vcplay https://open.spotify.com/track/...</code>\n"
                "<code>/vcplay https://soundcloud.com/...</code></blockquote>"
            ),
            parse_mode=ParseMode.HTML,
        )
    msg = await update.message.reply_text(
        apply_pe(f"<blockquote>🔍 <b>ꜱᴇᴀʀᴄʜɪɴɢ:</b> <i>{q}</i>...</blockquote>"),
        parse_mode=ParseMode.HTML,
    )
    await _stream_audio_vc(update.effective_chat.id, q, msg)


async def vplay_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle /vplay — stream VIDEO to group VC. Shows video in voice chat."""
    if update.effective_chat.type == "private":
        return await update.message.reply_text(
            apply_pe("❗ <b>VC ꜰᴇᴀᴛᴜʀᴇ ꜱɪʀꜰ ɢʀᴏᴜᴘ ᴍᴇ ᴋᴀᴀᴍ ᴋᴀʀᴛᴀ ʜᴀɪ!</b>"),
            parse_mode=ParseMode.HTML,
        )
    q = " ".join(ctx.args).strip() if ctx.args else ""
    if not q:
        return await update.message.reply_text(
            apply_pe(
                "<blockquote>❗ <b>ᴠɪᴅᴇᴏ ᴋᴀ ɴᴀᴀᴍ ʟɪᴋʜᴏ!</b>\n"
                "<code>/vplay Tum Hi Ho MV</code>\n"
                "<code>/vplay https://youtu.be/...</code></blockquote>"
            ),
            parse_mode=ParseMode.HTML,
        )
    msg = await update.message.reply_text(
        apply_pe(f"<blockquote>🎬 <b>ᴠɪᴅᴇᴏ ꜱᴇᴀʀᴄʜɪɴɢ:</b> <i>{q}</i>...</blockquote>"),
        parse_mode=ParseMode.HTML,
    )
    await _stream_video_vc(update.effective_chat.id, q, msg)


async def vcstop_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle /vcstop — leave the voice chat."""
    if update.effective_chat.type == "private":
        return await update.message.reply_text(
            apply_pe("❗ <b>VC ꜰᴇᴀᴛᴜʀᴇ ꜱɪʀꜰ ɢʀᴏᴜᴘ ᴍᴇ ᴋᴀᴀᴍ ᴋᴀʀᴛᴀ ʜᴀɪ!</b>"),
            parse_mode=ParseMode.HTML,
        )
    cid = update.effective_chat.id
    if not vc.is_ready():
        return await update.message.reply_text(
            apply_pe("❌ <b>VC ᴄʟɪᴇɴᴛ ʀᴇᴀᴅʏ ɴᴀʜɪ.</b>"), parse_mode=ParseMode.HTML
        )
    await vc.leave(cid)
    VC_ACTIVE.pop(cid, None)
    await update.message.reply_text(
        apply_pe(
            "<blockquote>⏹ <b>VC ꜱᴇ ʙᴀʜᴀʀ ʜᴏ ɢᴀʏᴀ!</b>\n"
            "<i>ᴅᴏʙᴀʀᴀ ꜱᴜɴɴᴇ ᴋᴇ ʟɪʏᴇ /vcplay ᴋᴀʀᴏ 🎵</i></blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💍 MARRY SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def marry_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    proposer = update.effective_user
    msg      = update.message

    # Must reply to someone OR mention someone
    target = None
    if msg.reply_to_message:
        target = msg.reply_to_message.from_user
    elif ctx.args:
        # try to get via mention entity
        for ent in msg.entities or []:
            if ent.type == "text_mention":
                target = ent.user
                break
        if not target:
            return await msg.reply_text(
                "❗ <b>Kisi ko reply karke /marry likho!</b>",
                parse_mode=ParseMode.HTML)

    if not target:
        return await msg.reply_text(
            "❗ <b>Kisi ko reply karke /marry karo!</b>\n"
            "<i>Example: kisi ke message pe reply karke /marry likho</i>",
            parse_mode=ParseMode.HTML)

    if target.id == proposer.id:
        return await msg.reply_text(
            "😂 <b>Apne aap se shaadi nahi kar sakte!</b>",
            parse_mode=ParseMode.HTML)

    if target.is_bot:
        return await msg.reply_text(
            "🤖 <b>Bot se shaadi nahi ho sakti!</b>",
            parse_mode=ParseMode.HTML)

    if is_married(proposer.id):
        sp = get_spouse(proposer.id)
        return await msg.reply_text(
            f"💔 <b>Aap pehle se shaadi-shuda ho!</b>\n\n"
            f"<b>🌸 Aapke Spouse:</b> <a href='tg://user?id={sp['spouse_id']}'>{sp['spouse_name']}</a>\n"
            f"<b>⏳ Since:</b> <code>{marriage_duration(sp['since'])}</code>\n\n"
            f"<i>Pehle /divorce karo phir kisi se shaadi karo.</i>",
            parse_mode=ParseMode.HTML)

    if is_married(target.id):
        sp = get_spouse(target.id)
        return await msg.reply_text(
            f"💔 <b>{target.first_name} pehle se kisi ke saath married hai!</b>\n"
            f"<i>Woh free nahi hai. 🥀</i>",
            parse_mode=ParseMode.HTML)

    # Store pending proposal
    PENDING_PROPOSALS[proposer.id] = target.id

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("💍 ʜᴀᴀɴ, ᴍᴀɴᴢᴏᴏʀ ʜᴀɪ! ✅", callback_data=f"marry:yes:{proposer.id}"),
        InlineKeyboardButton("💔 ɴᴀʜɪ, ᴍᴀᴀꜰ ᴋᴀʀᴏ ❌",  callback_data=f"marry:no:{proposer.id}"),
    ]])

    await msg.reply_text(
        apply_pe(
            f"✦ ❝ 💍 ꜱʜᴀᴀᴅɪ ᴋᴀ ᴘʀᴏᴘᴏꜱᴀʟ ❞ ✦\n\n"
            f"<blockquote>"
            f"💗 <a href='tg://user?id={proposer.id}'><b>{proposer.first_name}</b></a> ne\n"
            f"💌 <a href='tg://user?id={target.id}'><b>{target.first_name}</b></a> ko propose kiya!\n\n"
            f"🌸 <i>Kya aap is rishte ko qubool karte ho?</i>\n\n"
            f"⚠️ <i>Sirf</i> <a href='tg://user?id={target.id}'>{target.first_name}</a> <i>hi jawab de sakti/sakta hai!</i>"
            f"</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=kb,
    )


async def divorce_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_married(user.id):
        return await update.message.reply_text(
            "❗ <b>Aap abhi married nahi hain!</b>",
            parse_mode=ParseMode.HTML)

    sp = get_spouse(user.id)
    divorce(user.id)
    await update.message.reply_text(
        apply_pe(
            f"✦ ❝ 💔 ᴛᴀʟᴀǫ ❞ ✦\n\n"
            f"<blockquote>"
            f"😔 <b>{user.first_name}</b> aur\n"
            f"💔 <b>{sp['spouse_name']}</b> ka rishta khatam ho gaya.\n\n"
            f"⏳ <b>Saath tha :</b> <code>{marriage_duration(sp['since'])}</code>"
            f"</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )


async def spouse_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Check for reply or self
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else user

    if not is_married(target.id):
        name = "Aap" if target.id == user.id else target.first_name
        return await update.message.reply_text(
            f"💔 <b>{name} abhi tak kisi se married nahi hain!</b>",
            parse_mode=ParseMode.HTML)

    sp = get_spouse(target.id)
    dur       = marriage_duration(sp["since"])
    sp_id     = sp["spouse_id"]
    sp_name   = sp["spouse_name"]
    await update.message.reply_text(
        apply_pe(
            f"✦ ❝ 💍 ꜱʜᴀᴀᴅɪ ᴋɪ ᴊᴀᴀɴᴋᴀᴀʀɪ ❞ ✦\n\n"
            f"<blockquote>"
            f"💗 <b>User   :</b> <a href='tg://user?id={target.id}'>{target.first_name}</a>\n"
            f"💌 <b>Spouse :</b> <a href='tg://user?id={sp_id}'>{sp_name}</a>\n"
            f"⏳ <b>Saath  :</b> <code>{dur}</code>\n\n"
            f"🌸 <i>Yeh ek pyaara rishta hai!</i>"
            f"</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )


async def marriages_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    pairs = all_marriages()
    if not pairs:
        return await update.message.reply_text(
            "💔 <b>Abhi koi bhi married nahi hai!</b>\n"
            "<i>Pehle couple bano 💍</i>",
            parse_mode=ParseMode.HTML)

    lines = "\n".join(
        f"  ✦ <b>{i}.</b> 💗 <b>{p['user1_name']}</b> ❤️ <b>{p['user2_name']}</b> "
        f"<i>({marriage_duration(p['since'])})</i>"
        for i, p in enumerate(pairs[:15], 1)
    )
    await update.message.reply_text(
        apply_pe(
            f"✦ ❝ 💍 ꜱʜᴀᴀᴅɪꜱʜᴜᴅᴀ ᴊᴏᴅɪʏᴀᴀɴ ❞ ✦\n\n"
            f"<blockquote>"
            f"{lines}\n\n"
            f"👫 <i>ᴛᴏᴛᴀʟ ᴄᴏᴜᴘʟᴇꜱ : {len(pairs)}</i>"
            f"</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GREETING HELPERS — TAG ALL MEMBERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_GREET_HEADERS = {
    "gm":        ("🌅", "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ", "ɴᴀʏᴀ ꜱᴀᴠᴇʀᴀ, ɴᴀʏɪ ᴜᴍᴍᴇᴇᴅ! ☀️"),
    "gn":        ("🌙", "ɢᴏᴏᴅ ɴɪɢʜᴛ",   "ᴀᴀʀᴀᴍ ᴋᴀʀᴏ, ᴋᴀʟ ꜰɪʀ ᴍɪʟᴇɴɢᴇ! 💤"),
    "afternoon": ("☀️",  "ɢᴏᴏᴅ ᴀꜰᴛᴇʀɴᴏᴏɴ","ᴅᴏᴘᴀʜᴀʀ ᴋɪ ꜱʜᴜʙʜ ᴋᴀᴍɴᴀᴇɴ! 🌞"),
    "lunch":     ("🍽️", "ʟᴜɴᴄʜ ᴛɪᴍᴇ!",  "ᴋʜᴀɴᴀ ᴋʜᴀᴀ ʟᴏ ʙʜᴀɪ! 😋"),
    "dinner":    ("🌆", "ᴅɪɴɴᴇʀ ᴛɪᴍᴇ!", "ʀᴀᴀᴛ ᴋᴀ ᴋʜᴀɴᴀ ʜᴏ ɢᴀʏᴀ? 🍛"),
}

async def _send_greeting(update: Update, key: str):
    chat  = update.effective_chat
    if chat is None or chat.type == "private":
        return await update.message.reply_text(
            "❌ <b>Yeh command sirf groups mein kaam karta hai!</b>",
            parse_mode=ParseMode.HTML)

    emoji, title, tagline = _GREET_HEADERS[key]
    members = get_members(chat.id)

    if not members:
        return await update.message.reply_text(
            f"{emoji} <b>{title}!</b>\n\n"
            "<i>Abhi koi member track nahi hua. Group mein thodi baat ho toh tags milenge!</i>",
            parse_mode=ParseMode.HTML)

    # Build tag chunks — max ~20 tags per message to avoid flood
    CHUNK = 20
    for i in range(0, len(members), CHUNK):
        chunk = members[i : i + CHUNK]
        tags  = "  ".join(
            "<a href='tg://user?id={uid}'>{name}</a>".format(uid=m["user_id"], name=m["name"])
            for m in chunk
        )
        is_first = (i == 0)
        if is_first:
            header = apply_pe(
                f"✦ ❝ {emoji} {title} ❞ ✦\n\n"
                f"<blockquote>"
                f"⌯ <i>{tagline}</i>\n\n"
                f"👥 <b>ᴍᴇᴍʙᴇʀꜱ ᴛᴀɢ :</b>\n"
                f"{tags}"
                f"</blockquote>"
            )
            await update.message.reply_text(header, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(
                apply_pe(f"<blockquote>{emoji} ᴄᴏɴᴛɪɴᴜᴇᴅ...\n{tags}</blockquote>"),
                parse_mode=ParseMode.HTML)


async def gm_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _send_greeting(update, "gm")

async def gn_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _send_greeting(update, "gn")

async def afternoon_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _send_greeting(update, "afternoon")

async def lunch_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _send_greeting(update, "lunch")

async def dinner_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _send_greeting(update, "dinner")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CALLBACK HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def button_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    async def _edit(text: str, markup=None):
        """Edit caption if message has photo, else edit text. Auto-applies premium emoji."""
        text = apply_pe(text)
        try:
            await q.edit_message_caption(
                caption=text, parse_mode=ParseMode.HTML, reply_markup=markup)
        except Exception:
            try:
                await q.edit_message_text(
                    text, parse_mode=ParseMode.HTML, reply_markup=markup,
                    disable_web_page_preview=True)
            except Exception:
                pass

    if d == "cmd:home":
        name = q.from_user.first_name or "User"
        await _edit(start_text(name), home_keyboard())

    elif d == "cmd:magic":
        await _edit(MAGIC_TEXT, cmds_keyboard(0))

    elif d.startswith("cmd:cmds_"):
        page = int(d.split("_")[-1])
        await _edit(CMDS_HEADER, cmds_keyboard(page))

    elif d == "cmd:version":
        kb = [[InlineKeyboardButton("ᴛᴀᴘ ᴛᴏ ꜱᴇᴇ ᴠᴇʀꜱɪᴏɴ ɪɴꜰᴏ ↗", url="https://t.me/ABOUTxYUTAA")],
              [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="cmd:home")]]
        await _edit(VERSION_TEXT, InlineKeyboardMarkup(kb))

    elif d == "cmd:master":
        await _edit(
            "✦ ❝ 👹 ᴍʏ ᴍᴀꜱᴛᴇʀ ❞ ✦\n\n"
            "<blockquote>"
            "⌯ <b>ᴄʀᴇᴀᴛᴇᴅ ʙʏ ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ</b>\n\n"
            "🎀 <i>ᴍᴀʀʀʏ ᴍᴜꜱɪᴄ ʙᴏᴛ ᴋᴇ ᴘɪᴛᴀ ᴊɪ!</i>\n"
            "💬 <i>ꜱᴜᴘᴘᴏʀᴛ ᴋᴇ ʟɪʏᴇ ᴅᴇᴠ ꜱᴇ ᴍɪʟᴏ ↗</i>"
            "</blockquote>",
            InlineKeyboardMarkup([[
                InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ ↗", url="https://t.me/Zcziiyy"),
                InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="cmd:home"),
            ]]))

    elif d == "cmd:cancel":
        await _edit("❌ <b>ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")

    elif d.startswith("c:"):
        key   = d[2:]
        usage = _CMD_USAGE.get(key, "")
        if usage:
            await q.answer(
                f"📌 {usage}\n\n💡 ʏᴇ ᴄᴏᴍᴍᴀɴᴅ ᴛᴀʏᴘ ᴋᴀʀᴏ ᴀᴜʀ ᴜꜱᴇ ᴋᴀʀᴏ!",
                show_alert=True
            )
        else:
            await q.answer("⏳ ᴄᴏᴍɪɴɢ ꜱᴏᴏɴ! 🚀", show_alert=True)

    elif d == "noop":
        await q.answer("ʏᴇ ᴀʙʜɪ ᴜᴘᴅᴀᴛᴇ ʜᴏ ʀᴀʜᴀ ʜᴀɪ!", show_alert=False)

    elif d.startswith("dl:"):
        parts = d.split(":", 2)
        video_id = parts[1]
        title    = parts[2] if len(parts) > 2 else video_id
        await q.delete_message()
        await _download_and_send(q.message, video_id, title)

    elif d.startswith("vc:"):
        parts    = d.split(":", 3)
        video_id = parts[2]
        title    = parts[3] if len(parts) > 3 else video_id
        await q.delete_message()
        await _stream_to_vc(q.message.chat_id, video_id, title, q.message)

    elif d.startswith("marry:"):
        parts      = d.split(":")
        action     = parts[1]           # yes / no
        proposer_id = int(parts[2])
        responder  = q.from_user

        # Only the target (the one who was proposed to) can respond
        expected_target = PENDING_PROPOSALS.get(proposer_id)
        if expected_target is None:
            return await q.answer("⏰ Yeh proposal expire ho gaya!", show_alert=True)
        if responder.id != expected_target:
            return await q.answer("❌ Yeh proposal tumhare liye nahi hai!", show_alert=True)

        PENDING_PROPOSALS.pop(proposer_id, None)

        if action == "no":
            await q.edit_message_text(
                apply_pe(
                    f"✦ ❝ 💔 ᴘʀᴏᴘᴏꜱᴀʟ ʀᴇᴊᴇᴄᴛ ❞ ✦\n\n"
                    f"<blockquote>"
                    f"😔 <b>{responder.first_name}</b> ne proposal ❌ reject kar diya...\n\n"
                    f"💔 <i>Dil toot gaya bhai!</i>"
                    f"</blockquote>"
                ),
                parse_mode=ParseMode.HTML,
            )
            return

        # action == "yes" — actually marry them
        proposer_info = await q.get_bot().get_chat(proposer_id)
        proposer_name = proposer_info.first_name or "Unknown"

        success = marry(proposer_id, proposer_name, responder.id, responder.first_name)
        if not success:
            await q.edit_message_text(
                apply_pe("✦ ❝ ❌ ᴇʀʀᴏʀ ❞ ✦\n\n<blockquote>❌ <b>Shaadi nahi ho saki!</b>\n<i>Dono mein se koi pehle se married hai.</i></blockquote>"),
                parse_mode=ParseMode.HTML)
            return

        await q.edit_message_text(
            apply_pe(
                f"✦ ❝ 💍 ꜱʜᴀᴀᴅɪ ʜᴏ ɢᴀʏɪ! 🎉 ❞ ✦\n\n"
                f"<blockquote>"
                f"💗 <a href='tg://user?id={proposer_id}'><b>{proposer_name}</b></a>\n"
                f"❤️ &amp;\n"
                f"💌 <a href='tg://user?id={responder.id}'><b>{responder.first_name}</b></a>\n\n"
                f"🌸 <i>Ab yeh dono ek hain!</i>\n"
                f"🎊 <i>Congratulations! Mubaarak ho!</i>\n\n"
                f"⌯ <i>/spouse se partner dekho | /divorce se alag ho sakte ho</i>"
                f"</blockquote>"
            ),
            parse_mode=ParseMode.HTML,
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👑 OWNER COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def broadcast_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Owner only: /broadcast <msg> — send to all known groups."""
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text(
            apply_pe("❌ <b>ꜱɪʀꜰ ᴏᴡɴᴇʀ ᴋᴀʀ ꜱᴀᴋᴛᴀ ʜᴀɪ!</b>"), parse_mode=ParseMode.HTML
        )
    text = " ".join(ctx.args).strip() if ctx.args else ""
    if update.message.reply_to_message:
        text = update.message.reply_to_message.text or text
    if not text:
        return await update.message.reply_text(
            apply_pe("<blockquote>❗ <b>ᴍᴇꜱꜱᴀɢᴇ ᴅᴏ!</b>\n<code>/broadcast Aap sabko pyar ❤️</code></blockquote>"),
            parse_mode=ParseMode.HTML,
        )
    from YUKIYTAPI.database.members import get_all_chat_ids
    chats = get_all_chat_ids()
    done = fail = 0
    status_msg = await update.message.reply_text(
        apply_pe(f"<blockquote>📡 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱᴛᴀʀᴛ...</b> {len(chats)} ɢʀᴏᴜᴘꜱ</blockquote>"),
        parse_mode=ParseMode.HTML,
    )
    for cid in chats:
        try:
            await ctx.bot.send_message(
                chat_id=cid,
                text=apply_pe(text),
                parse_mode=ParseMode.HTML,
            )
            done += 1
        except Exception:
            fail += 1
    await status_msg.edit_text(
        apply_pe(
            f"<blockquote>✅ <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴏɴᴇ!</b>\n"
            f"✔️ ꜱᴜᴄᴄᴇꜱꜱ: <code>{done}</code>\n"
            f"❌ ꜰᴀɪʟᴇᴅ: <code>{fail}</code></blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )
    await log_event(
        ctx.bot,
        f"<blockquote>📡 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ</b> ʙʏ ᴏᴡɴᴇʀ\n✔️ {done} • ❌ {fail}\n💬 <i>{text[:80]}</i></blockquote>",
    )


async def gban_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Owner only: /gban @user — globally ban a user from all groups."""
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text(
            apply_pe("❌ <b>ꜱɪʀꜰ ᴏᴡɴᴇʀ ᴋᴀʀ ꜱᴀᴋᴛᴀ ʜᴀɪ!</b>"), parse_mode=ParseMode.HTML
        )
    target = None
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    elif ctx.args:
        try:
            target = await ctx.bot.get_chat(ctx.args[0].lstrip("@"))
        except Exception:
            pass
    if not target:
        return await update.message.reply_text(
            apply_pe("<blockquote>❗ <b>User reply karo ya @username do!</b></blockquote>"),
            parse_mode=ParseMode.HTML,
        )
    from YUKIYTAPI.database.members import get_all_chat_ids
    chats = get_all_chat_ids()
    done = 0
    for cid in chats:
        try:
            await ctx.bot.ban_chat_member(chat_id=cid, user_id=target.id)
            done += 1
        except Exception:
            pass
    ulink = f"<a href='tg://user?id={target.id}'><b>{target.first_name}</b></a>"
    await update.message.reply_text(
        apply_pe(
            f"<blockquote>🚫 <b>ɢʟᴏʙᴀʟ ʙᴀɴ ᴅᴏɴᴇ!</b>\n"
            f"👤 ᴜꜱᴇʀ: {ulink}\n"
            f"📊 {done} ɢʀᴏᴜᴘꜱ ꜱᴇ ʙᴀɴ ʜᴜᴀ</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )
    await log_event(
        ctx.bot,
        f"<blockquote>🚫 <b>ɢʙᴀɴ</b>\n👤 {ulink} (<code>{target.id}</code>)\n📊 {done} ɢʀᴏᴜᴘꜱ</blockquote>",
    )


async def logs_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Owner only: /logs — show bot stats for owner."""
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text(
            apply_pe("❌ <b>ꜱɪʀꜰ ᴏᴡɴᴇʀ ᴋᴀʀ ꜱᴀᴋᴛᴀ ʜᴀɪ!</b>"), parse_mode=ParseMode.HTML
        )
    s = get_system_stats()
    try:
        from YUKIYTAPI.database.members import get_all_chat_ids
        total_chats = len(get_all_chat_ids())
    except Exception:
        total_chats = 0
    marriages_count = len(all_marriages())
    await update.message.reply_text(
        apply_pe(
            f"<blockquote>"
            f"👑 <b>ᴏᴡɴᴇʀ ꜱᴛᴀᴛꜱ ᴘᴀɴᴇʟ</b>\n\n"
            f"📊 <b>ꜱʏꜱᴛᴇᴍ</b>\n"
            f"🌸 ᴜᴘᴛɪᴍᴇ : <code>{s['uptime']}</code>\n"
            f"🌸 ᴄᴘᴜ    : <code>{s['cpu']}%</code>\n"
            f"🌸 ʀᴀᴍ    : <code>{s['ram']}%</code>\n\n"
            f"🤖 <b>ʙᴏᴛ</b>\n"
            f"🌸 ɢʀᴏᴜᴘꜱ : <code>{total_chats}</code>\n"
            f"🌸 ᴍᴀʀʀɪᴀɢᴇꜱ : <code>{marriages_count}</code>\n"
            f"🌸 ᴠᴄ ʀᴇᴀᴅʏ : <code>{'✅' if vc.is_ready() else '❌'}</code>\n\n"
            f"📋 ʟᴏɢ ɢʀᴏᴜᴘ: <code>{LOG_CHAT_ID}</code>\n"
            f"👑 ᴏᴡɴᴇʀ ɪᴅ : <code>{OWNER_ID}</code>"
            f"</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )


async def owner_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Owner only: /owner — show owner panel with all commands."""
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text(
            apply_pe("❌ <b>ꜱɪʀꜰ ᴏᴡɴᴇʀ ᴋᴀʀ ꜱᴀᴋᴛᴀ ʜᴀɪ!</b>"), parse_mode=ParseMode.HTML
        )
    await update.message.reply_text(
        apply_pe(
            f"<blockquote>"
            f"👑 <b>ᴏᴡɴᴇʀ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ</b>\n\n"
            f"📡 /broadcast [ᴍꜱɢ] — ꜱᴀʙ ɢʀᴏᴜᴘ ᴍᴇ ᴍᴇꜱꜱᴀɢᴇ\n"
            f"🚫 /gban @ᴜꜱᴇʀ — ɢʟᴏʙᴀʟ ʙᴀɴ\n"
            f"📋 /logs — ʙᴏᴛ ꜱᴛᴀᴛꜱ\n"
            f"🆔 /chatid — ᴄᴜʀʀᴇɴᴛ ᴄʜᴀᴛ ɪᴅ\n\n"
            f"<i>⌯ ʏᴇ ꜱᴀʙ ꜱɪʀꜰ ᴏᴡɴᴇʀ ᴋᴇ ʟɪʏᴇ ʜᴀɪɴ</i>"
            f"</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📋 ʟᴏɢꜱ", callback_data="owner:logs"),
            InlineKeyboardButton("📡 ʙʀᴏᴀᴅᴄᴀꜱᴛ", callback_data="owner:bc_help"),
        ]]),
    )


async def chatid_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Get current chat ID — useful for setup."""
    cid  = update.effective_chat.id
    uid  = update.effective_user.id
    name = update.effective_chat.title or update.effective_user.first_name
    await update.message.reply_text(
        apply_pe(
            f"<blockquote>"
            f"🆔 <b>ɪᴅ ɪɴꜰᴏ</b>\n\n"
            f"📍 ᴄʜᴀᴛ ɪᴅ : <code>{cid}</code>\n"
            f"👤 ᴜꜱᴇʀ ɪᴅ : <code>{uid}</code>\n"
            f"📛 ɴᴀᴍᴇ   : <b>{name}</b>"
            f"</blockquote>"
        ),
        parse_mode=ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def _post_init(application):
    """Called after bot is initialized — start VC client here."""
    logger.info("🎧 VC client init ho raha hai...")
    await vc.init()
    if vc.is_ready():
        logger.info("✅ VC client ready!")
    else:
        logger.warning("⚠️  VC client ready nahi hua — SESSION_SECRET check karo.")


def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN set nahi hai!")
        return

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(_post_init)
        .build()
    )

    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("help",      help_cmd))
    app.add_handler(CommandHandler("play",      play_cmd))
    app.add_handler(CommandHandler("song",      song_cmd))
    app.add_handler(CommandHandler("stats",     stats_cmd))
    app.add_handler(CommandHandler("ping",      ping_cmd))
    # 🎵 VC commands
    app.add_handler(CommandHandler("vcplay",    vc_play_cmd))
    app.add_handler(CommandHandler("vplay",     vplay_cmd))
    app.add_handler(CommandHandler("vcstop",    vcstop_cmd))
    # 💍 Marry system
    app.add_handler(CommandHandler("marry",     marry_cmd))
    app.add_handler(CommandHandler("divorce",   divorce_cmd))
    app.add_handler(CommandHandler("spouse",    spouse_cmd))
    app.add_handler(CommandHandler("marriages", marriages_cmd))
    # 🌅 Greeting / Tag All Members
    app.add_handler(CommandHandler(["gm", "goodmorning"],                  gm_cmd))
    app.add_handler(CommandHandler(["gn", "goodnight"],                    gn_cmd))
    app.add_handler(CommandHandler(["ga", "goodafternoon", "afternoon"],   afternoon_cmd))
    app.add_handler(CommandHandler(["lunch", "lunchtime"],                 lunch_cmd))
    app.add_handler(CommandHandler(["dinner", "dinnertime"],               dinner_cmd))
    # 👑 Owner commands
    app.add_handler(CommandHandler("broadcast",  broadcast_cmd))
    app.add_handler(CommandHandler("gban",       gban_cmd))
    app.add_handler(CommandHandler("logs",       logs_cmd))
    app.add_handler(CommandHandler("owner",      owner_cmd))
    app.add_handler(CommandHandler("chatid",     chatid_cmd))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("🤖 MARRY Music Bot start ho raha hai...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
