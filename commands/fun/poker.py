import random
from database import get_balance, update_balance

POKER_DATA = {
    "name": "poker",
    "description": "Bet chips and play Video Poker",
    "type": 1,
    "options": [{
        "name": "bet",
        "description": "Amount to bet",
        "type": 4, # Typ 4 to Integer (liczba całkowita)
        "required": True
    }]
}

SUITS = ["♠️", "♥️", "♦️", "♣️"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
VALUES = {r: i for i, r in enumerate(RANKS, 2)}

def get_hand_result(hand):
    hand.sort(key=lambda c: VALUES[c['rank']])
    ranks = [c['rank'] for c in hand]
    suits = [c['suit'] for c in hand]
    unique_ranks = set(ranks)
    is_flush = len(set(suits)) == 1
    indices = [VALUES[r] for r in ranks]
    is_straight = indices == list(range(min(indices), max(indices)+1))
    if set(ranks) == {"A", "2", "3", "4", "5"}: is_straight = True
    
    counts = {r: ranks.count(r) for r in unique_ranks}
    count_values = sorted(counts.values(), reverse=True)

    # Zwracamy: (Nazwa, Mnożnik, Kolor)
    if is_flush and is_straight:
        if "A" in ranks and "10" in ranks: return "👑 Royal Flush!", 250, 0xdfb404
        return "🔥 Straight Flush!", 50, 0xe74c3c
    if 4 in count_values: return "💣 Four of a Kind!", 25, 0x9b59b6
    if 3 in count_values and 2 in count_values: return "🏠 Full House!", 9, 0x3498db
    if is_flush: return "💧 Flush!", 6, 0x1abc9c
    if is_straight: return "📏 Straight!", 4, 0x2ecc71
    if 3 in count_values: return "3️⃣ Three of a Kind!", 3, 0xe67e22
    if count_values.count(2) == 2: return "2️⃣ Two Pair!", 2, 0xf1c40f
    
    # Jacks or Better (Para waletów lub wyższa zwraca zakład - x1)
    if 2 in count_values:
        # Sprawdź jaka to para
        for rank, count in counts.items():
            if count == 2 and VALUES[rank] >= 11: # 11 = Jack
                return "1️⃣ Pair (Jacks+)", 1, 0x95a5a6
        return "1️⃣ Small Pair", 0, 0x2b2d31 # Mała para przegrywa

    return "💨 High Card", 0, 0x2b2d31

def cmd_poker(data):
    # 1. Dane gracza
    member = data.get("member", {})
    user = member.get("user", {})
    user_id = user.get("id")
    username = user.get("username", "Player")
    
    # 2. Pobierz zakład
    options = data.get("options", [])
    bet = 0
    for opt in options:
        if opt["name"] == "bet":
            bet = opt["value"]
            
    if bet <= 0:
        return {"type": 4, "data": {"content": "❌ You must bet at least $1."}}

    # 3. Sprawdź pieniądze w bazie
    current_balance = get_balance(user_id)
    if current_balance < bet:
        return {"type": 4, "data": {"content": f"❌ **You're broke!** You have ${current_balance}, but tried to bet ${bet}. Use `/daily`!"}}

    # 4. Gra (Zabierz zakład)
    update_balance(user_id, -bet)
    
    deck = [{'rank': r, 'suit': s} for s in SUITS for r in RANKS]
    random.shuffle(deck)
    hand = deck[:5]
    
    hand_name, multiplier, color = get_hand_result(hand)
    winnings = bet * multiplier
    
    # 5. Wypłać nagrodę (jeśli wygrał)
    if winnings > 0:
        update_balance(user_id, winnings)
        result_msg = f"**WINNER!** You won **${winnings}**"
    elif multiplier == 1: # Zwrot (Jacks or Better)
        # Jacks or better w tej wersji to zazwyczaj zwrot albo x2, tutaj dałem x1 jako zwrot
        # update_balance(user_id, bet) # Już dodane wyżej jako winnings = bet * 1
        result_msg = f"**PUSH** (Money back)"
    else:
        result_msg = f"**LOST** (-${bet})"

    new_balance = get_balance(user_id) # Pobierz aktualny stan po grze

    cards_display = " ".join([f"`{c['rank']}{c['suit']}`" for c in hand])

    return {
        "type": 4,
        "data": {
            "embeds": [
                {
                    "title": "🎰 Clavin Casino Poker",
                    "description": f"**{username}** bet **${bet}**\n\n{cards_display}\n\n**{hand_name}**\n{result_msg}\n\n💰 New Balance: **${new_balance}**",
                    "color": color
                }
            ]
        }
    }