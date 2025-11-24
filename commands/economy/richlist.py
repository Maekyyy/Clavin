from database import get_leaderboard

# ZMIANA NAZWY Z LEADERBOARD NA RICHLIST
RICHLIST_DATA = {
    "name": "richlist",
    "description": "Show the wealthiest users (Top 10)",
    "type": 1
}

def cmd_richlist(data):
    top_users = get_leaderboard(10)
    
    desc = ""
    for i, user in enumerate(top_users, 1):
        data = user.to_dict()
        balance = data.get('balance', 0)
        medal = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
        desc += f"**{medal}** <@{user.id}>: **${balance}**\n"

    if not desc:
        desc = "No data yet."

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "💎 Richest Players", # Zmieniony tytuł
                "description": desc,
                "color": 0xf1c40f # Złoty
            }]
        }
    }