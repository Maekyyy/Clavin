import time
from database import get_full_profile

PROFILE_DATA = {
    "name": "profile",
    "description": "Check user profile (Stats, Money, Items)",
    "type": 1,
    "options": [{
        "name": "user",
        "description": "Whose profile?",
        "type": 6, # User
        "required": False
    }]
}

def cmd_profile(data):
    # Sprawdź czy podano usera, czy siebie
    if data.get("options"):
        target_id = data["options"][0]["value"]
        # Pobierz dane usera z resolved (dla avatara i nicku)
        resolved = data.get("resolved", {}).get("users", {}).get(target_id, {})
        username = resolved.get("username", "Unknown")
        avatar = resolved.get("avatar")
    else:
        user = data["member"]["user"]
        target_id = user["id"]
        username = user["username"]
        avatar = user["avatar"]

    # Pobierz dane z bazy
    profile = get_full_profile(target_id)
    
    # Wyciągnij wartości (z domyślnymi zerami)
    balance = profile.get("balance", 0)
    crypto = profile.get("crypto", 0)
    level = profile.get("level", 1)
    xp = profile.get("xp", 0)
    title = profile.get("title", "Novice")
    inventory = profile.get("inventory", [])
    partner_id = profile.get("partner_id")
    marriage_date = profile.get("marriage_date")

    # Formatowanie
    inv_str = ", ".join([i.title() for i in inventory]) if inventory else "Empty"
    
    desc = f"👑 **Title:** {title}\n"
    desc += f"⭐ **Level:** {level} ({xp} XP)\n"
    desc += f"💰 **Cash:** ${balance:,}\n"
    desc += f"🪙 **Crypto:** {crypto} CC\n"
    desc += f"🎒 **Items:** {inv_str}\n"
    
    if partner_id:
        timestamp = f"<t:{marriage_date}:R>" if marriage_date else ""
        desc += f"💍 **Married to:** <@{partner_id}> {timestamp}\n"
    else:
        desc += "💔 **Status:** Single\n"

    # Avatar URL
    if avatar:
        av_url = f"https://cdn.discordapp.com/avatars/{target_id}/{avatar}.png"
    else:
        av_url = ""

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": f"👤 Profile: {username}",
                "description": desc,
                "color": 0x3498db,
                "thumbnail": {"url": av_url}
            }]
        }
    }