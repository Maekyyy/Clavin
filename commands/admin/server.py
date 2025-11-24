import os
import requests

SERVER_DATA = {
    "name": "serverinfo",
    "description": "Show detailed server information",
    "type": 1
}

def cmd_server_info(data):
    # 1. Pobieramy Token i ID (potrzebne do zapytania API)
    token = os.environ.get("DISCORD_BOT_TOKEN")
    guild_id = data.get("guild_id")

    if not guild_id:
        return {"type": 4, "data": {"content": "❌ Error: Could not determine Guild ID."}}

    # 2. Przygotowujemy nagłówki dla Discord API
    headers = {"Authorization": f"Bot {token}"}
    base_url = "https://discord.com/api/v10"

    # 3. POBIERAMY DANE O SERWERZE (Szczegóły, właściciel, liczba członków)
    # Parametr with_counts=true jest kluczowy!
    r_guild = requests.get(f"{base_url}/guilds/{guild_id}?with_counts=true", headers=headers)
    
    if r_guild.status_code != 200:
        return {"type": 4, "data": {"content": f"❌ Error fetching guild data: {r_guild.status_code}"}}
    
    g = r_guild.json() # 'g' to obiekt z danymi serwera

    # 4. POBIERAMY DANE O KANAŁACH (Żeby je policzyć)
    r_channels = requests.get(f"{base_url}/guilds/{guild_id}/channels", headers=headers)
    channels = r_channels.json() if r_channels.status_code == 200 else []

    # --- PRZETWARZANIE DANYCH (MATEMATYKA) ---

    # Liczenie kanałów
    text_count = len([c for c in channels if c["type"] == 0]) # 0 = Text
    voice_count = len([c for c in channels if c["type"] == 2]) # 2 = Voice
    category_count = len([c for c in channels if c["type"] == 4]) # 4 = Category

    # Role
    roles = g.get("roles", [])
    roles_count = len(roles)
    
    # Sortujemy role (od najwyższej) i usuwamy @everyone
    sorted_roles = sorted(roles, key=lambda x: x["position"], reverse=True)
    role_mentions = [f"<@&{r['id']}>" for r in sorted_roles if r["name"] != "@everyone"]
    
    # Formatowanie listy ról (żeby nie była za długa)
    if len(role_mentions) > 20:
        roles_display = ", ".join(role_mentions[:20]) + f" ...and {len(role_mentions)-20} more"
    else:
        roles_display = ", ".join(role_mentions) if role_mentions else "None"

    # Emojis
    emojis = g.get("emojis", [])
    static_emojis = len([e for e in emojis if not e.get("animated", False)])
    animated_emojis = len([e for e in emojis if e.get("animated", False)])

    # Daty i inne
    # Używamy specjalnego formatowania Discorda <t:TIMESTAMP:F> -> Pokaże datę w języku użytkownika!
    # 'id' serwera to timestamp (snowflake), ale prościej wziąć datę z API jeśli dostępna,
    # lub po prostu wyświetlić ID. Discord API nie zwraca wprost "created_at" w tym endpoincie
    # bez obliczeń na bitach, więc dla uproszczenia wyświetlimy ID.
    
    # Obrazek serwera (Icon URL)
    icon_url = ""
    if g.get("icon"):
        icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{g['icon']}.png"

    # 5. BUDOWANIE EMBEDA (Wygląd a'la Dyno)
    return {
        "type": 4,
        "data": {
            "embeds": [
                {
                    "title": g.get("name", "Server Info"),
                    "color": 0x2b2d31, # Ciemny kolor tła (jak w Dyno)
                    "thumbnail": {"url": icon_url},
                    "fields": [
                        {
                            "name": "Owner",
                            "value": f"<@{g['owner_id']}>",
                            "inline": True
                        },
                        {
                            "name": "Members",
                            "value": str(g.get("approximate_member_count", "Unknown")),
                            "inline": True
                        },
                        {
                            "name": "Roles",
                            "value": str(roles_count),
                            "inline": True
                        },
                        {
                            "name": "Category Channels",
                            "value": str(category_count),
                            "inline": True
                        },
                        {
                            "name": "Text Channels",
                            "value": str(text_count),
                            "inline": True
                        },
                        {
                            "name": "Voice Channels",
                            "value": str(voice_count),
                            "inline": True
                        },
                        {
                            "name": "Emojis",
                            "value": f"Static: {static_emojis} | Animated: {animated_emojis} | Total: {len(emojis)}",
                            "inline": False
                        },
                        {
                            "name": f"Role List ({len(role_mentions)})",
                            "value": roles_display,
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": f"ID: {guild_id}"
                    }
                }
            ]
        }
    }