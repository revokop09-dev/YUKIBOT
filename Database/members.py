"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ʏᴜᴋɪ — ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀ ᴛʀᴀᴄᴋᴇʀ
  Stores members who talk in groups
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json, os

DB_PATH = os.path.join(os.path.dirname(__file__), "group_members.json")


def _load() -> dict:
    if not os.path.exists(DB_PATH):
        return {}
    try:
        with open(DB_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)


def add_member(chat_id: int, user_id: int, first_name: str, username: str = ""):
    data = _load()
    cid  = str(chat_id)
    if cid not in data:
        data[cid] = {}
    data[cid][str(user_id)] = {
        "name":     first_name,
        "username": username or "",
    }
    _save(data)


def get_members(chat_id: int) -> list[dict]:
    data    = _load()
    cid     = str(chat_id)
    members = data.get(cid, {})
    return [
        {"user_id": int(uid), "name": info["name"], "username": info.get("username", "")}
        for uid, info in members.items()
    ]


def member_count(chat_id: int) -> int:
    return len(get_members(chat_id))


def get_all_chat_ids() -> list[int]:
    """Return all known group/chat IDs where members were tracked."""
    data = _load()
    return [int(cid) for cid in data.keys()]
