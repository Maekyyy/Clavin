from database import transfer_item, get_inventory

GIFT_DATA = {
    "name": "gift",
    "description": "Give an item to another player",
    "type": 1,
    "options": [
        {
            "name": "user",
            "description": "Recipient",
            "type": 6, # User
            "required": True
        },
        {
            "name": "item",
            "description": "Item ID (e.g. shield, lockpick)",
            "type": 3, # String
            "required": True,
            "choices": [
                {"name": "🛡️ Shield", "value": "shield"},
                {"name": "🧷 Lockpick", "value": "lockpick"},
                {"name": "🆔 Fake ID", "value": "fake_id"},
                {"name": "💊 Vitamins", "value": "vitamins"}
            ]
        }
    ]
}

def cmd_gift(data):
    sender_id = data["member"]["user"]["id"]
    options = data.get("options", [])
    
    target_id = options[0]["value"]
    item_id = options[1]["value"]
    
    if sender_id == target_id:
        return {"type": 4, "data": {"content": "❌ You cannot gift yourself."}}
        
    success, msg = transfer_item(sender_id, target_id, item_id)
    
    if success:
        return {
            "type": 4,
            "data": {
                "content": f"🎁 **Gift Sent!**\nYou gave a **{item_id.upper()}** to <@{target_id}>."
            }
        }
    else:
        return {"type": 4, "data": {"content": f"❌ **Error:** {msg}"}}