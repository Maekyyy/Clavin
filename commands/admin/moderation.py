import os
import requests

# --- DEFINICJE KOMEND (Z uprawnieniami) ---

# Permission flag: MANAGE_MESSAGES (0x2000)
CLEAR_DATA = {
    "name": "clear",
    "description": "Delete recent messages",
    "type": 1,
    "default_member_permissions": "8192", # Wymaga Manage Messages
    "options": [{
        "name": "amount",
        "description": "Number of messages to delete (max 100)",
        "type": 4, # Integer
        "required": True,
        "min_value": 1,
        "max_value": 100
    }]
}

# Permission flag: KICK_MEMBERS (0x2)
KICK_DATA = {
    "name": "kick",
    "description": "Kick a user from the server",
    "type": 1,
    "default_member_permissions": "2", # Wymaga Kick Members
    "options": [
        {"name": "user", "description": "User to kick", "type": 6, "required": True},
        {"name": "reason", "description": "Reason for kick", "type": 3, "required": False}
    ]
}

# Permission flag: BAN_MEMBERS (0x4)
BAN_DATA = {
    "name": "ban",
    "description": "Ban a user from the server",
    "type": 1,
    "default_member_permissions": "4", # Wymaga Ban Members
    "options": [
        {"name": "user", "description": "User to ban", "type": 6, "required": True},
        {"name": "reason", "description": "Reason for ban", "type": 3, "required": False}
    ]
}

# --- LOGIKA ---

def cmd_clear(data):
    # Potrzebujemy channel_id z interakcji
    channel_id = data.get("channel_id")
    token = os.environ.get("DISCORD_BOT_TOKEN")
    
    # Pobierz ilość (z opcji)
    amount = data["options"][0]["value"]
    
    headers = {"Authorization": f"Bot {token}"}
    base_url = "https://discord.com/api/v10"

    # 1. Pobierz ID ostatnich wiadomości
    # Fetch amount + 1 (bo API liczy też samą komendę, choć slash command nie jest wiadomością, lepiej mieć zapas)
    r_get = requests.get(f"{base_url}/channels/{channel_id}/messages?limit={amount}", headers=headers)
    
    if r_get.status_code != 200:
        return {"type": 4, "data": {"content": "❌ Error fetching messages."}}
    
    messages = r_get.json()
    msg_ids = [m["id"] for m in messages]
    
    if not msg_ids:
        return {"type": 4, "data": {"content": "❌ No messages found to delete."}}

    # 2. Wyślij żądanie Bulk Delete
    # Uwaga: To działa tylko dla wiadomości młodszych niż 14 dni
    r_del = requests.post(
        f"{base_url}/channels/{channel_id}/messages/bulk-delete", 
        headers=headers, 
        json={"messages": msg_ids}
    )

    if r_del.status_code == 204:
        return {"type": 4, "data": {"content": f"🧹 **Cleared {len(msg_ids)} messages.**"}}
    else:
        return {"type": 4, "data": {"content": "❌ Error deleting messages (Are they older than 14 days?)."}}

def cmd_kick(data):
    guild_id = data.get("guild_id")
    target_id = data["options"][0]["value"]
    reason = "No reason provided"
    if len(data["options"]) > 1:
        reason = data["options"][1]["value"]
        
    token = os.environ.get("DISCORD_BOT_TOKEN")
    headers = {"Authorization": f"Bot {token}"}
    
    # Wywołanie API: DELETE /guilds/{guild.id}/members/{user.id}
    url = f"https://discord.com/api/v10/guilds/{guild_id}/members/{target_id}"
    
    r = requests.delete(url, headers=headers, json={"reason": reason})
    
    if r.status_code == 204:
        return {"type": 4, "data": {"content": f"👢 **Kicked** <@{target_id}>\n📝 Reason: {reason}"}}
    else:
        return {"type": 4, "data": {"content": f"❌ Failed to kick user. Check my permissions (Move my role higher!). Code: {r.status_code}"}}

def cmd_ban(data):
    guild_id = data.get("guild_id")
    target_id = data["options"][0]["value"]
    reason = "No reason provided"
    if len(data["options"]) > 1:
        reason = data["options"][1]["value"]
        
    token = os.environ.get("DISCORD_BOT_TOKEN")
    headers = {"Authorization": f"Bot {token}"}
    
    # Wywołanie API: PUT /guilds/{guild.id}/bans/{user.id}
    url = f"https://discord.com/api/v10/guilds/{guild_id}/bans/{target_id}"
    
    r = requests.put(url, headers=headers, json={"reason": reason})
    
    if r.status_code == 204:
        return {"type": 4, "data": {"content": f"🔨 **Banned** <@{target_id}>\n📝 Reason: {reason}"}}
    else:
        return {"type": 4, "data": {"content": f"❌ Failed to ban user. Check my permissions. Code: {r.status_code}"}}