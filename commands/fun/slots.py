import random
from database import get_balance, update_balance

SLOTS_DATA = {
    "name": "slots",
    "description": "Spin the slot machine",
    "type": 1,
    "options": [{
        "name": "bet",
        "description": "Amount to bet",
        "type": 4,
        "required": True
    }]
}

ICONS = ["🍒", "🍋", "🍇", "🔔", "💎", "7️⃣"]

def cmd_slots(data):
    user_id = data["member"]["user"]["id"]
    
    # Pobierz bet
    options = data.get("options", [])
    bet = options[0]["value"] if options else 0
    
    if bet < 1: return {"type": 4, "data": {"content": "❌ Bet too low."}}
    if get_balance(user_id) < bet: return {"type": 4, "data": {"content": "❌ Not enough money."}}

    update_balance(user_id, -bet)

    # Losowanie 3 symboli
    row = [random.choice(ICONS) for _ in range(3)]
    
    # Sprawdzanie wygranej
    winnings = 0
    result_msg = "LOST"
    
    # 3 takie same
    if row[0] == row[1] == row[2]:
        if row[0] == "7️⃣": winnings = bet * 50  # Jackpot
        elif row[0] == "💎": winnings = bet * 20
        else: winnings = bet * 10
        result_msg = "JACKPOT!"
    # 2 takie same
    elif row[0] == row[1] or row[1] == row[2] or row[0] == row[2]:
        winnings = int(bet * 1.5)
        result_msg = "Small Win"

    if winnings > 0:
        update_balance(user_id, winnings)
        desc = f"**{result_msg}!** You won **${winnings}**"
        color = 0x2ecc71 # Zielony
    else:
        desc = f"Better luck next time!"
        color = 0xe74c3c # Czerwony

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "🎰 Slot Machine",
                "description": f"Bet: ${bet}\n\n> | {row[0]} | {row[1]} | {row[2]} |\n\n{desc}",
                "color": color
            }]
        }
    }