import random
from database import get_balance, update_balance

# --- DEFINICJA KOMENDY ---
ROULETTE_DATA = {
    "name": "roulette",
    "description": "Play Casino Roulette",
    "type": 1,
    "options": [
        {
            "name": "amount",
            "description": "Amount to bet",
            "type": 4, # Integer
            "required": True
        },
        {
            "name": "bet_on",
            "description": "What to bet on? (red, black, even, odd, 1-18, 19-36, or number 0-36)",
            "type": 3, # String
            "required": True
        }
    ]
}

# --- LOGIKA RULETKI ---
# Numery czerwone w ruletce europejskiej
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

def get_number_details(number):
    """Zwraca kolor i emoji dla wylosowanej liczby."""
    if number == 0:
        return "green", "🟢"
    elif number in RED_NUMBERS:
        return "red", "🔴"
    else:
        return "black", "⚫"

def check_win(number, bet_type):
    """Sprawdza czy gracz wygrał. Zwraca mnożnik wygranej."""
    bet_type = bet_type.lower().strip()
    
    # 1. Zakład na konkretną liczbę (np. "17", "0")
    if bet_type.isdigit():
        target = int(bet_type)
        if 0 <= target <= 36:
            if number == target:
                return 36 # Wypłata x36 (czysty zysk x35)
            return 0
    
    # Dane o wylosowanej liczbie
    color, _ = get_number_details(number)
    is_even = (number % 2 == 0) and (number != 0)
    is_odd = (number % 2 != 0)
    
    # 2. Zakłady zewnętrzne (Outside Bets) - Wypłata x2
    if bet_type in ["red", "czerwone", "r"] and color == "red": return 2
    if bet_type in ["black", "czarne", "b"] and color == "black": return 2
    
    if bet_type in ["even", "parzyste"] and is_even: return 2
    if bet_type in ["odd", "nieparzyste"] and is_odd: return 2
    
    if bet_type in ["1-18", "low", "niskie"] and (1 <= number <= 18): return 2
    if bet_type in ["19-36", "high", "wysokie"] and (19 <= number <= 36): return 2

    return 0

# --- GŁÓWNA FUNKCJA ---
def cmd_roulette(data):
    # 1. Pobierz dane użytkownika
    user = data["member"]["user"]
    user_id = user["id"]
    username = user["username"]

    # 2. Pobierz opcje
    options = data.get("options", [])
    amount = 0
    bet_on = ""
    
    for opt in options:
        if opt["name"] == "amount": amount = opt["value"]
        if opt["name"] == "bet_on": bet_on = str(opt["value"])

    # 3. Walidacja pieniędzy
    if amount <= 0:
        return {"type": 4, "data": {"content": "❌ Bet must be greater than 0."}}
    
    balance = get_balance(user_id)
    if balance < amount:
        return {"type": 4, "data": {"content": f"❌ You don't have enough chips! Balance: ${balance}"}}

    # 4. Gra - Zabieramy zakład
    update_balance(user_id, -amount)
    
    # Losowanie (0-36)
    winning_number = random.randint(0, 36)
    res_color, res_emoji = get_number_details(winning_number)
    
    # Sprawdzenie wygranej
    multiplier = check_win(winning_number, bet_on)
    winnings = amount * multiplier
    
    # 5. Wynik
    if winnings > 0:
        update_balance(user_id, winnings)
        title = "🎉 WINNER!"
        desc = f"Ball landed on: **{res_emoji} {winning_number}**\n\nYou won **${winnings}**!"
        color = 0x2ecc71 # Zielony
    else:
        title = "💀 LOST"
        desc = f"Ball landed on: **{res_emoji} {winning_number}**\n\nBetter luck next time!"
        color = 0xe74c3c # Czerwony

    new_balance = get_balance(user_id)

    return {
        "type": 4,
        "data": {
            "embeds": [
                {
                    "title": f"🎰 Roulette | {username}",
                    "description": f"Bet: **${amount}** on **{bet_on}**\n\n{desc}\n\n💰 Wallet: **${new_balance}**",
                    "color": color,
                    "thumbnail": {
                        "url": "https://i.imgur.com/2Y8n5O5.png" # Obrazek koła ruletki
                    }
                }
            ]
        }
    }