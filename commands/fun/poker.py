import random

# --- DEFINICJA KOMENDY ---
POKER_DATA = {
    "name": "poker",
    "description": "Play a quick hand of 5-Card Poker",
    "type": 1
}

# --- LOGIKA GRY ---
SUITS = ["♠️", "♥️", "♦️", "♣️"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
VALUES = {r: i for i, r in enumerate(RANKS, 2)}

def get_hand_rank(hand):
    # Sortujemy karty po wartości
    hand.sort(key=lambda c: VALUES[c['rank']])
    
    ranks = [c['rank'] for c in hand]
    suits = [c['suit'] for c in hand]
    unique_ranks = set(ranks)
    is_flush = len(set(suits)) == 1
    
    # Sprawdzanie strita (kolejne wartości)
    indices = [VALUES[r] for r in ranks]
    is_straight = indices == list(range(min(indices), max(indices)+1))
    
    # Specjalny przypadek strita: A, 2, 3, 4, 5
    if set(ranks) == {"A", "2", "3", "4", "5"}:
        is_straight = True

    # Liczenie powtórzeń (np. ile jest asów, ile króli)
    counts = {r: ranks.count(r) for r in unique_ranks}
    count_values = sorted(counts.values(), reverse=True)

    # OCENA RĘKI
    if is_flush and is_straight:
        if "A" in ranks and "10" in ranks: return "👑 Royal Flush!", 0xdfb404 # Złoty
        return "🔥 Straight Flush!", 0xe74c3c # Czerwony
    
    if 4 in count_values: return "💣 Four of a Kind!", 0x9b59b6 # Fioletowy
    if 3 in count_values and 2 in count_values: return "🏠 Full House!", 0x3498db # Niebieski
    if is_flush: return "💧 Flush!", 0x1abc9c # Turkusowy
    if is_straight: return "📏 Straight!", 0x2ecc71 # Zielony
    if 3 in count_values: return "3️⃣ Three of a Kind!", 0xe67e22 # Pomarańczowy
    if count_values.count(2) == 2: return "2️⃣ Two Pair!", 0xf1c40f # Żółty
    if 2 in count_values: return "1️⃣ Pair!", 0x95a5a6 # Szary
    
    return "💨 High Card (Nothing)", 0x2b2d31 # Ciemny

def cmd_poker(data):
    # 1. Generujemy talię i losujemy 5 kart
    deck = [{'rank': r, 'suit': s} for s in SUITS for r in RANKS]
    random.shuffle(deck)
    hand = deck[:5]
    
    # 2. Oceniamy rękę
    result_text, color = get_hand_rank(hand)
    
    # 3. Formatujemy wygląd kart
    cards_display = " ".join([f"`{c['rank']}{c['suit']}`" for c in hand])
    
    # Wyciągamy imię gracza
    member = data.get("member", {})
    user = member.get("user", {})
    username = user.get("username", "Player")

    return {
        "type": 4,
        "data": {
            "embeds": [
                {
                    "title": "🎰 Video Poker",
                    "description": f"**{username}'s Hand:**\n\n{cards_display}\n\n**Result:**\n# {result_text}",
                    "color": color,
                    "footer": {"text": "One-shot poker • Google Cloud Run"}
                }
            ]
        }
    }