from database import get_balance, update_balance, add_item, get_inventory

SHOP_DATA = {
    "name": "shop",
    "description": "Buy items or check inventory",
    "type": 1,
    "options": [
        {
            "name": "action",
            "description": "What to do?",
            "type": 3,
            "required": True,
            "choices": [
                {"name": "List Items", "value": "list"},
                {"name": "Buy Shield ($500)", "value": "buy_shield"},
                {"name": "My Inventory", "value": "inv"}
            ]
        }
    ]
}

def cmd_shop(data):
    user_id = data["member"]["user"]["id"]
    action = data["options"][0]["value"]

    if action == "list":
        return {
            "type": 4,
            "data": {
                "embeds": [{
                    "title": "🛒 Clavin Shop",
                    "description": "**Available Items:**\n\n🛡️ **Shield** - `$500`\nProtects you from one robbery.\n\n*More items coming soon!*",
                    "color": 0x3498db
                }]
            }
        }

    if action == "inv":
        items = get_inventory(user_id)
        if not items:
            items_str = "Empty (You are vulnerable!)"
        else:
            items_str = ", ".join([f"**{i.upper()}**" for i in items])
            
        return {"type": 4, "data": {"content": f"🎒 **Your Inventory:** {items_str}"}}

    if action == "buy_shield":
        price = 500
        if get_balance(user_id) < price:
            return {"type": 4, "data": {"content": "❌ Not enough money!"}}
        
        inv = get_inventory(user_id)
        if "shield" in inv:
            return {"type": 4, "data": {"content": "❌ You already have a Shield!"}}

        update_balance(user_id, -price)
        add_item(user_id, "shield")
        
        return {"type": 4, "data": {"content": "🛡️ **Bought a Shield!** You are safe from the next robbery."}}