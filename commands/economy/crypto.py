from database import get_balance, update_balance, get_crypto_price, get_crypto_balance, update_crypto

CRYPTO_DATA = {
    "name": "crypto",
    "description": "Trade ClavinCoin (CC)",
    "type": 1,
    "options": [
        {
            "name": "action",
            "description": "Buy, Sell or Check Price",
            "type": 3,
            "required": True,
            "choices": [
                {"name": "Check Price 📉", "value": "price"},
                {"name": "Buy CC 🟢", "value": "buy"},
                {"name": "Sell CC 🔴", "value": "sell"}
            ]
        },
        {
            "name": "amount",
            "description": "How many coins?",
            "type": 4,
            "required": False
        }
    ]
}

def cmd_crypto(data):
    user_id = data["member"]["user"]["id"]
    options = data.get("options", [])
    action = options[0]["value"]
    
    amount = 1
    if len(options) > 1:
        amount = options[1]["value"]

    price = get_crypto_price()
    current_cc = get_crypto_balance(user_id)
    current_cash = get_balance(user_id)

    if action == "price":
        return {
            "type": 4,
            "data": {
                "embeds": [{
                    "title": "📈 ClavinCoin Market",
                    "description": f"Current Price: **${price}** / CC\n\nYour Wallet:\n💵 **${current_cash}**\n🪙 **{current_cc} CC**",
                    "color": 0x3498db
                }]
            }
        }

    if amount <= 0:
        return {"type": 4, "data": {"content": "❌ Amount must be positive."}}

    cost = price * amount

    if action == "buy":
        if current_cash < cost:
            return {"type": 4, "data": {"content": f"❌ You need **${cost}** but have **${current_cash}**."}}
        
        update_balance(user_id, -cost)
        update_crypto(user_id, amount)
        return {"type": 4, "data": {"content": f"🟢 **Bought {amount} CC** for **${cost}**."}}

    if action == "sell":
        if current_cc < amount:
            return {"type": 4, "data": {"content": f"❌ You only have **{current_cc} CC**."}}
            
        update_balance(user_id, cost)
        update_crypto(user_id, -amount)
        return {"type": 4, "data": {"content": f"🔴 **Sold {amount} CC** for **${cost}**."}}