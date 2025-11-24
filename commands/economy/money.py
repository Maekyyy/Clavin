# Dodajemy check_cooldown do importów
from database import get_balance, claim_daily, check_cooldown
from database import get_balance, claim_daily, check_cooldown, get_title

# --- DEFINICJA BALANCE (Bez zmian) ---
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
    title = get_title(user_id) # Pobierz tytuł
    
# Jeśli ma tytuł, dodaj go przed nickiem
    display_name = f"[{title}] {user['username']}" if title else user['username']
    
    return {
        "type": 4,
        "data": {
            "content": f"💰 **{display_name}**, you have **${money}** chips."
        }
    }

# --- DEFINICJA DAILY (Z NAPRAWIONĄ BLOKADĄ) ---
DAILY_DATA = {
    "name": "daily",
    "description": "Collect your daily 1000 chips",
    "type": 1
}

def cmd_daily(data):
    member = data.get("member", {})
    user = member.get("user", {})
    user_id = user.get("id")
    
    # 1. Sprawdź cooldown (86400 sekund = 24 godziny)
    # Funkcja check_cooldown musi być w database.py!
    can_claim, time_left = check_cooldown(user_id, "daily", 86400)
    
    if not can_claim:
        # Obliczamy ile czasu zostało
        hours = int(time_left // 3600)
        minutes = int((time_left % 3600) // 60)
        
        return {
            "type": 4,
            "data": {
                "content": f"⏳ **Hol' up!** You already claimed your daily reward.\nCome back in **{hours}h {minutes}m**."
            }
        }

    # 2. Jeśli można odebrać -> Wypłać
    new_balance = claim_daily(user_id)
    
    return {
        "type": 4,
        "data": {
            "content": f"💵 **Ka-ching!** You received **$1000**. Current balance: **${new_balance}**"
        }
    }