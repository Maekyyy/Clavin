from database import get_balance, claim_daily

# --- DEFINICJA BALANCE ---
BALANCE_DATA = {
    "name": "balance",
    "description": "Check your wallet balance",
    "type": 1
}

def cmd_balance(data):
    member = data.get("member", {})
    user = member.get("user", {})
    user_id = user.get("id")
    
    money = get_balance(user_id)
    
    return {
        "type": 4,
        "data": {
            "content": f"💰 **{user['username']}**, you have **${money}** chips."
        }
    }

# --- DEFINICJA DAILY ---
DAILY_DATA = {
    "name": "daily",
    "description": "Collect your daily 1000 chips",
    "type": 1
}

def cmd_daily(data):
    member = data.get("member", {})
    user = member.get("user", {})
    user_id = user.get("id")
    
    new_balance = claim_daily(user_id)
    
    return {
        "type": 4,
        "data": {
            "content": f"💵 **Ka-ching!** You received **$1000**. Current balance: **${new_balance}**"
        }
    }