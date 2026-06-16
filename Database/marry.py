"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ʏᴜᴋɪ ᴍᴀʀʀʏ ᴅᴀᴛᴀʙᴀꜱᴇ
  JSON-based marriage storage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json, os, time

DB_PATH = os.path.join(os.path.dirname(__file__), "marriages.json")


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


def get_spouse(user_id: int) -> dict | None:
    """Return spouse info dict or None."""
    data = _load()
    return data.get(str(user_id))


def is_married(user_id: int) -> bool:
    return get_spouse(user_id) is not None


def marry(user1_id: int, user1_name: str, user2_id: int, user2_name: str) -> bool:
    """Create marriage between two users. Returns False if either is already married."""
    if is_married(user1_id) or is_married(user2_id):
        return False
    data = _load()
    ts = int(time.time())
    data[str(user1_id)] = {
        "spouse_id":   user2_id,
        "spouse_name": user2_name,
        "own_name":    user1_name,
        "since":       ts,
    }
    data[str(user2_id)] = {
        "spouse_id":   user1_id,
        "spouse_name": user1_name,
        "own_name":    user2_name,
        "since":       ts,
    }
    _save(data)
    return True


def divorce(user_id: int) -> bool:
    """Remove marriage. Returns False if not married."""
    data = _load()
    info = data.get(str(user_id))
    if not info:
        return False
    spouse_id = str(info["spouse_id"])
    data.pop(str(user_id), None)
    data.pop(spouse_id, None)
    _save(data)
    return True


def all_marriages() -> list[dict]:
    """Return list of unique couples."""
    data  = _load()
    seen  = set()
    pairs = []
    for uid, info in data.items():
        sid = str(info["spouse_id"])
        key = tuple(sorted([uid, sid]))
        if key not in seen:
            seen.add(key)
            pairs.append({
                "user1_id":   int(uid),
                "user1_name": info["own_name"],
                "user2_id":   int(sid),
                "user2_name": info["spouse_name"],
                "since":      info["since"],
            })
    return pairs


def marriage_duration(since: int) -> str:
    """Return human-readable duration since timestamp."""
    diff = int(time.time()) - since
    d, r = divmod(diff, 86400)
    h, r = divmod(r, 3600)
    m, _ = divmod(r, 60)
    if d > 0:
        return f"{d}d {h}h {m}m"
    elif h > 0:
        return f"{h}h {m}m"
    else:
        return f"{m}m"
