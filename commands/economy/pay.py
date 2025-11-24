from database import transfer_money

PAY_DATA = {
    "name": "pay",
    "description": "Transfer chips to another user",
    "type": 1,
    "options": [
        {
            "name": "user",
            "description": "User to pay",
            "type": 6, # Typ USER
            "required": True
        },
        {
            "name": "amount",
            "description": "Amount to transfer",
            "type": 4, # Typ INTEGER
            "required": True
        }
    ]
}

def cmd_pay(data):
    sender_id = data["member"]["user"]["id"]
    options = data.get("options", [])
    
    target_id = None
    amount = 0
    
    for opt in options:
        if opt["name"] == "user": target_id = opt["value"]
        if opt["name"] == "amount": amount = opt["value"]

    # Walidacja
    if amount <= 0:
        return {"type": 4, "data": {"content": "❌ Amount must be positive."}}
    
    if str(sender_id) == str(target_id):
        return {"type": 4, "data": {"content": "❌ You cannot pay yourself."}}

    # Wykonaj przelew
    success, msg = transfer_money(sender_id, target_id, amount)
    
    if success:
        return {
            "type": 4,
            "data": {
                "content": f"💸 **Transfer Successful!**\nSent **${amount}** to <@{target_id}>."
            }
        }
    else:
        return {"type": 4, "data": {"content": f"❌ Error: {msg}"}}