SERVER_DATA = {
    "name": "serverinfo",
    "description": "Show basic server information",
    "type": 1
}

def cmd_server_info(data):
    guild_id = data.get("guild_id", "Unknown (DM?)")
    
    # Try to get username
    member = data.get("member", {})
    user = member.get("user", {})
    username = user.get("username", "Stranger")

    return {
        "type": 4,
        "data": {
            "embeds": [
                {
                    "title": "📊 Server Info",
                    "color": 0x00ff00,
                    "fields": [
                        {"name": "Server ID", "value": str(guild_id), "inline": True},
                        {"name": "Triggered by", "value": username, "inline": True},
                        {"name": "Code Location", "value": "commands/admin/server.py", "inline": False}
                    ],
                    "footer": {"text": "Running on Google Cloud Run"}
                }
            ]
        }
    }