import random
from database import get_balance, update_balance

RPS_DATA = {
    "name": "rps",
    "description": "Play Rock Paper Scissors",
    "type": 1,
    "options": [
        {
            "name": "sign",
            "description": "Pick your move",
            "type": 3,
            "required": True,
            "choices": [
                {"name": "🪨 Rock", "value": "rock"},
                {"name": "📄 Paper", "value": "paper"},
                {"name": "✂️ Scissors", "value": "scissors"}
            ]
        },
        {
            "name": "bet",
            "description": "Amount to bet",
            "type": 4,
            "required": True
        }
    ]
}

def cmd_rps(data):
    user_id = data["member"]["user"]["id"]
    options = data.get("options", [])
    
    sign = options[0]["value"]
    bet = options[1]["value"]
    
    if bet < 1: return {"type": 4, "data": {"content": "❌ Invalid bet."}}
    if get_balance(user_id) < bet: return {"type": 4, "data": {"content": "❌ You are broke."}}
    
    update_balance(user_id, -bet)
    
    bot_sign = random.choice(["rock", "paper", "scissors"])
    emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    
    # Logika gry
    result = "tie"
    if sign == bot_sign:
        result = "tie"
    elif (sign == "rock" and bot_sign == "scissors") or \
         (sign == "paper" and bot_sign == "rock") or \
         (sign == "scissors" and bot_sign == "paper"):
        result = "win"
    else:
        result = "lose"
        
    # Wynik
    if result == "win":
        winnings = bet * 2
        update_balance(user_id, winnings)
        msg = f"**YOU WON!** (+${winnings})"
        color = 0x2ecc71
    elif result == "tie":
        update_balance(user_id, bet) # Zwrot
        msg = "**TIE!** (Money back)"
        color = 0xf1c40f
    else:
        msg = f"**YOU LOST!** (-${bet})"
        color = 0xe74c3c
        
    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "✂️ Rock Paper Scissors",
                "description": f"You: {emojis[sign]}\nBot: {emojis[bot_sign]}\n\n{msg}",
                "color": color
            }]
        }
    }