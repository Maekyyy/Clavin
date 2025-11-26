from database import get_balance, get_bank_balance, bank_transaction

BANK_DATA = {
    "name": "bank",
    "description": "Manage your bank account (Safe from robbery)",
    "type": 1,
    "options": [
        {
            "name": "action",
            "description": "Deposit, Withdraw or Check Balance",
            "type": 3,
            "required": True,
            "choices": [
                {"name": "Balance 🏦", "value": "balance"},
                {"name": "Deposit 📥", "value": "deposit"},
                {"name": "Withdraw 📤", "value": "withdraw"}
            ]
        },
        {
            "name": "amount",
            "description": "Amount (or type 0 for all)",
            "type": 4,
            "required": False
        }
    ]
}

def cmd_bank(data):
    user_id = data["member"]["user"]["id"]
    options = data.get("options", [])
    action = options[0]["value"]
    amount = options[1]["value"] if len(options) > 1 else "all"
    
    if action == "balance":
        cash = get_balance(user_id)
        bank = get_bank_balance(user_id)
        total = cash + bank
        
        return {
            "type": 4,
            "data": {
                "embeds": [{
                    "title": "🏦 Bank of Clavin",
                    "color": 0x3498db,
                    "fields": [
                        {"name": "💵 Wallet", "value": f"${cash:,}", "inline": True},
                        {"name": "💳 Bank", "value": f"${bank:,}", "inline": True},
                        {"name": "💰 Net Worth", "value": f"${total:,}", "inline": True},
                        {"name": "📈 Interest", "value": "2% daily (Max $5k)", "inline": False}
                    ]
                }]
            }
        }

    # Deposit / Withdraw
    success, msg = bank_transaction(user_id, amount, action)
    
    if success:
        return {"type": 4, "data": {"content": f"✅ **{msg}**"}}
    else:
        return {"type": 4, "data": {"content": f"❌ **Error:** {msg}"}}