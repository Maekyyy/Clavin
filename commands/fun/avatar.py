AVATAR_DATA = {
    "name": "avatar",
    "description": "Show user avatar",
    "type": 1,
    "options": [{
        "name": "user",
        "description": "Which user?",
        "type": 6, # User
        "required": True
    }]
}

def cmd_avatar(data):
    # Wyciągamy ID użytkownika z opcji
    target_id = data["options"][0]["value"]
    
    # Wyciągamy dane użytkownika z sekcji 'resolved' (Discord wysyła tu szczegóły)
    resolved = data.get("resolved", {}).get("users", {}).get(target_id, {})
    
    username = resolved.get("username", "Unknown")
    avatar_hash = resolved.get("avatar")
    user_id = resolved.get("id")

    if not avatar_hash:
        # Domyślny avatar jeśli user nie ma ustawionego
        avatar_url = f"https://cdn.discordapp.com/embed/avatars/{int(user_id) % 5}.png"
    else:
        # Budujemy URL (obsługa GIFów)
        ext = "gif" if avatar_hash.startswith("a_") else "png"
        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{ext}?size=1024"

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": f"🖼️ Avatar: {username}",
                "image": {"url": avatar_url},
                "color": 0x3498db,
                "footer": {"text": "Click image to open full size"}
            }]
        }
    }