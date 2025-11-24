from database import get_level_data, get_xp_leaderboard

RANK_DATA = {
    "name": "rank",
    "description": "Check your Level and XP",
    "type": 1,
    "options": [{
        "name": "user",
        "description": "Check someone else",
        "type": 6, # User
        "required": False
    }]
}

LEADERBOARD_XP_DATA = {
    "name": "leaderboard",
    "description": "Global Level Leaderboard",
    "type": 1
}

def cmd_rank(data):
    target_user = data["member"]["user"]
    # Sprawdź czy podano innego użytkownika
    if data.get("options"):
        target_id = data["options"][0]["value"]
        # Discord nie zawsze przesyła nick w opcjach, więc używamy resolved
        resolved = data.get("resolved", {}).get("users", {}).get(target_id, {})
        username = resolved.get("username", "Unknown")
    else:
        target_id = target_user["id"]
        username = target_user["username"]

    lvl, xp = get_level_data(target_id)
    xp_needed = lvl * 100
    progress = int((xp / xp_needed) * 10)
    bar = "🟦" * progress + "⬜" * (10 - progress)

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": f"⭐ Rank: {username}",
                "description": f"**Level {lvl}**\nXP: {xp} / {xp_needed}\n\n{bar}",
                "color": 0x9b59b6 # Fioletowy
            }]
        }
    }

def cmd_leaderboard_xp(data):
    top_users = get_xp_leaderboard(10)
    
    desc = ""
    for i, user in enumerate(top_users, 1):
        d = user.to_dict()
        lvl = d.get('level', 1)
        xp = d.get('xp', 0)
        medal = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
        desc += f"**{medal}** <@{user.id}> • **Lvl {lvl}** ({xp} XP)\n"

    if not desc: desc = "No data yet."

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "🏆 Level Leaderboard",
                "description": desc,
                "color": 0x9b59b6
            }]
        }
    }