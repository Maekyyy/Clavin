SERVER_DATA = {
    "name": "serverinfo",
    "description": "Pokaż podstawowe informacje o serwerze",
    "type": 1
}

def cmd_server_info(data):
    # W danych od Discorda mamy 'guild_id'
    guild_id = data.get("guild_id", "Nieznane (DM?)")
    
    # Możemy też wyciągnąć ID użytkownika, który wywołał komendę
    member = data.get("member", {})
    user = member.get("user", {})
    username = user.get("username", "Nieznajomy")

    return {
        "type": 4,
        "data": {
            "embeds": [
                {
                    "title": "📊 Server Info",
                    "color": 0x00ff00, # Zielony kolor
                    "fields": [
                        {"name": "Server ID", "value": str(guild_id), "inline": True},
                        {"name": "Wywołane przez", "value": username, "inline": True},
                        {"name": "Moduł", "value": "Admin", "inline": True}
                    ],
                    "footer": {"text": "Działam na Google Cloud Run"}
                }
            ]
        }
    }