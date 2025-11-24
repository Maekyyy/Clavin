from database import get_balance, update_balance, set_title, get_title

# Cennik
TITLES = {
    "Baron": 10000,
    "Duke": 50000,
    "King": 100000,
    "Emperor": 1000000,
    "Godlike": 5000000
}

BUY_TITLE_DATA = {
    "name": "buy_title",
    "description": "Buy a prestige title",
    "type": 1,
    "options": [{
        "name": "title",
        "description": "Select a title to buy",
        "type": 3, # String
        "required": True,
        "choices": [{"name": f"{name} (${price:,})", "value": name} for name, price in TITLES.items()]
    }]
}

def cmd_buy_title(data):
    user_id = data["member"]["user"]["id"]
    selected_title = data["options"][0]["value"]
    price = TITLES.get(selected_title)
    
    if not price:
        return {"type": 4, "data": {"content": "❌ Invalid title."}}

    # Sprawdź kasę
    if get_balance(user_id) < price:
        return {"type": 4, "data": {"content": f"❌ You need **${price:,}** for **{selected_title}**."}}

    # Sprawdź czy już ma ten tytuł
    current = get_title(user_id)
    if current == selected_title:
        return {"type": 4, "data": {"content": f"❌ You are already a **{selected_title}**!"}}

    # Kupno
    update_balance(user_id, -price)
    set_title(user_id, selected_title)
    
    return {
        "type": 4,
        "data": {
            "content": f"👑 **Congratulations!** You purchased the title **{selected_title}** for ${price:,}!"
        }
    }