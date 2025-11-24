import os
import requests

SERVER_DATA = {
    "name": "serverinfo",
    "description": "Show detailed server information",
    "type": 1
}

def cmd_server_info(data):
    token = os.environ.get("DISCORD_BOT_TOKEN")
    guild_id = data.get("guild_id")

    if not guild_id:
        return {"type": 4, "data": {"content": "❌ Error: Could not determine Guild ID."}}

    headers = {"Authorization": f"Bot {token}"}
    base_url = "https://discord.com/api/v10"

    # 1. POBIERANIE DANYCH
    r_guild = requests.get(f"{base_url}/guilds/{guild_id}?with_counts=true", headers=headers)
    
    if r_guild.status_code != 200:
        return {"type": 4, "data": {"content": f"❌ Error fetching guild data: {r_guild.status_code}"}}
    
    g = r_guild.json()

    # 2. POBIERANIE KANAŁÓW
    r_channels = requests.get(f"{base_url}/guilds/{guild_id}/channels", headers=headers)
    channels = r_channels.json() if r_channels.status_code == 200 else []

    # --- OBLICZENIA ---

    # Data utworzenia z ID (Snowflake Logic)
    # Przesuwamy bity i dodajemy Epokę Discorda (2015-01-01)
    snowflake = int(guild_id)
    created_timestamp = ((snowflake >> 22) + 1420070400000) / 1000
    # Format Discorda: <t:TIMESTAMP:F> wyświetli pełną datę w języku użytkownika
    created_str = f"<t:{int(created_timestamp)}:F> (<t:{int(created_timestamp)}:R>)"

    # Statystyki kanałów
    text_count = len([c for c in channels if c["type"] == 0])
    voice_count = len([c for c in channels if c["type"] == 2])
    category_count = len([c for c in channels if c["type"] == 4])

    # Role
    roles = g.get("roles", [])
    roles_count = len(roles)
    sorted_roles = sorted(roles, key=lambda x: x["position"], reverse=True)
    role_mentions = [f"<@&{r['id']}>" for r in sorted_roles if r["name"] != "@everyone"]
    
    if len(role_mentions) > 20:
        roles_display = ", ".join(role_mentions[:20]) + f" ...and {len(role_mentions)-20} more"
    else:
        roles_display = ", ".join(role_mentions) if role_mentions else "None"

    # Emojis
    emojis = g.get("emojis", [])
    static_emojis = len([e for e in emojis if not e.get("animated", False)])
    animated_emojis = len([e for e in emojis if e.get("animated", False)])

    # Ikona
    icon_url = ""
    if g.get("icon"):
        icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{g['icon']}.png"

    # --- BUDOWANIE EMBEDA ---
    return {
        "type": 4,
        "data": {
            "embeds": [
                {
                    "title": g.get("name", "Server Info"),
                    "color": 0x2b2d31,
                    "thumbnail": {"url": icon_url},
                    "fields": [
                        {
                            "name": "👑 Owner",
                            "value": f"<@{g['owner_id']}>",
                            "inline": True
                        },
                        {
                            "name": "👥 Members",
                            "value": str(g.get("approximate_member_count", "Unknown")),
                            "inline": True
                        },
                        {
                            "name": "📅 Server Created",  # <-- NOWE POLE
                            "value": created_str,
                            "inline": False  # False, żeby data zajęła całą szerokość
                        },
                        {
                            "name": "🎭 Roles",
                            "value": str(roles_count),
                            "inline": True
                        },
                        {
                            "name": "📂 Categories",
                            "value": str(category_count),
                            "inline": True
                        },
                        {
                            "name": "💬 Text Channels",
                            "value": str(text_count),
                            "inline": True
                        },
                        {
                            "name": "🔊 Voice Channels",
                            "value": str(voice_count),
                            "inline": True
                        },
                        {
                            "name": "😃 Emojis",
                            "value": f"Static: {static_emojis} | Animated: {animated_emojis} | Total: {len(emojis)}",
                            "inline": False
                        },
                        {
                            "name": f"📜 Role List ({len(role_mentions)})",
                            "value": roles_display,
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": f"ID: {guild_id} • Running on Google Cloud Run"
                    }
                }
            ]
        }
    }