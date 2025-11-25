import random
from database import get_balance, update_balance

COINFLIP_DATA = {
    "name": "coinflip",
    "description": "Flip a coin to double your bet",
    "type": 1,
    "options": [
        {
            "name": "bet",
            "description": "Amount to bet",
            "type": 4,
            "required": True
        },
        {
            "name": "side",
            "description": "Heads or Tails?",
            "type": 3,
            "required": True,
            "choices": [
                {"name": "Heads (Orzeł)", "value": "heads"},
                {"name": "Tails (Reszka)", "value": "tails"}
            ]
        }
    ]
}

def cmd_coinflip(data):
    user_id = data["member"]["user"]["id"]
    options = data.get("options", [])
    bet = options[0]["value"]
    choice = options[1]["value"]

    if bet < 1: return {"type": 4, "data": {"content": "❌ Bet positive amount."}}
    if get_balance(user_id) < bet: return {"type": 4, "data": {"content": "❌ You are broke."}}

    # Zabierz kasę
    update_balance(user_id, -bet)

    # Rzut
    outcome = random.choice(["heads", "tails"])
    
    if choice == outcome:
        winnings = bet * 2
        update_balance(user_id, winnings)
        msg = f"🪙 **{outcome.upper()}!** You won **${winnings}**!"
        color = 0x2ecc71
    else:
        msg = f"🪙 **{outcome.upper()}!** You lost **${bet}**."
        color = 0xe74c3c

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "Coinflip",
                "description": msg,
                "color": color
            }]
        }
    }