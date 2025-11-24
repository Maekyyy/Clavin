import random
from database import get_balance, update_balance, set_game_state, get_game_state, delete_game_state

# --- DEFINICJA KOMENDY ---
POKER_DATA = {
    "name": "poker",
    "description": "Play 5-Card Draw Poker (with swapping!)",
    "type": 1,
    "options": [{
        "name": "bet",
        "description": "Amount to bet",
        "type": 4, 
        "required": True
    }]
}

# --- STAŁE ---
SUITS = ["♠️", "♥️", "♦️", "♣️"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
VALUES = {r: i for i, r in enumerate(RANKS, 2)}

# --- LOGIKA KART ---
def get_deck():
    """Tworzy nową przetasowaną talię."""
    deck = [{'rank': r, 'suit': s} for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

def get_hand_result(hand):
    """Ocenia rękę i zwraca (Nazwa, Mnożnik, Kolor)."""
    hand_sorted = sorted(hand, key=lambda c: VALUES[c['rank']])
    ranks = [c['rank'] for c in hand_sorted]
    suits = [c['suit'] for c in hand_sorted]
    
    # Sprawdzanie układów
    is_flush = len(set(suits)) == 1
    
    indices = [VALUES[r] for r in ranks]
    is_straight = indices == list(range(min(indices), max(indices)+1))
    if set(ranks) == {"A", "2", "3", "4", "5"}: is_straight = True
    
    counts = {r: ranks.count(r) for r in set(ranks)}
    count_values = sorted(counts.values(), reverse=True)

    # Tabela wypłat (Lucky Mode)
    if is_flush and is_straight:
        if "A" in ranks and "10" in ranks: return "👑 Royal Flush!", 250, 0xdfb404
        return "🔥 Straight Flush!", 50, 0xe74c3c
    if 4 in count_values: return "💣 Four of a Kind!", 25, 0x9b59b6
    if 3 in count_values and 2 in count_values: return "🏠 Full House!", 10, 0x3498db
    if is_flush: return "💧 Flush!", 7, 0x1abc9c
    if is_straight: return "📏 Straight!", 5, 0x2ecc71
    if 3 in count_values: return "3️⃣ Three of a Kind!", 3, 0xe67e22
    if count_values.count(2) == 2: return "2️⃣ Two Pair!", 2, 0xf1c40f
    
    # Pary
    if 2 in count_values:
        is_high = any(count == 2 and VALUES[rank] >= 11 for rank, count in counts.items())
        if is_high: return "1️⃣ High Pair (Jacks+)", 1, 0x95a5a6 # Tylko zwrot (x1)
        return "1️⃣ Small Pair", 0, 0x2b2d31 # Przegrana (x0) - tak jest w prawdziwym draw pokerze!

    return "💨 High Card", 0, 0x2b2d31

# --- GENEROWANIE PRZYCISKÓW ---
def build_components(held_indices, game_over=False):
    """Tworzy przyciski pod kartami."""
    if game_over:
        return [] # Brak przycisków na koniec gry

    buttons = []
    # 5 Przycisków do kart
    for i in range(5):
        is_held = i in held_indices
        buttons.append({
            "type": 2, # Button
            "style": 3 if is_held else 2, # 3=Green (Held), 2=Grey (Default)
            "label": "HOLD" if is_held else "Card " + str(i+1),
            "custom_id": f"poker_hold_{i}"
        })
    
    # Przycisk DRAW (Wymień)
    draw_btn = {
        "type": 2,
        "style": 1, # Blurple (Niebieski)
        "label": "🎲 DRAW (Exchange)",
        "custom_id": "poker_draw"
    }

    # Układamy w rzędy (max 5 na rząd)
    return [
        {"type": 1, "components": buttons}, # Rząd 1: Karty
        {"type": 1, "components": [draw_btn]} # Rząd 2: Draw
    ]

# --- START GRY (/poker) ---
def cmd_poker(data):
    user = data["member"]["user"]
    user_id = user["id"]
    
    # Sprawdź czy gra już trwa
    if get_game_state(user_id):
        return {"type": 4, "data": {"content": "❌ Masz już otwartą grę! Dokończ ją najpierw."}}

    # Pobierz zakład
    bet = data["options"][0]["value"] if data.get("options") else 0
    
    # Sprawdź kasę
    if get_balance(user_id) < bet:
        return {"type": 4, "data": {"content": "❌ Nie masz tyle pieniędzy!"}}
    
    if bet < 1:
        return {"type": 4, "data": {"content": "❌ Zakład musi być większy niż 0."}}

    # Zabierz kasę
    update_balance(user_id, -bet)

    # Rozdaj karty
    deck = get_deck()
    hand = deck[:5]
    remaining_deck = deck[5:]

    # Zapisz stan do bazy
    game_data = {
        "bet": bet,
        "hand": hand,
        "deck": remaining_deck,
        "held": [] # Indeksy kart do zatrzymania
    }
    set_game_state(user_id, game_data)

    # Wyświetl
    cards_str = " ".join([f"`{c['rank']}{c['suit']}`" for c in hand])
    
    return {
        "type": 4,
        "data": {
            "content": f"🎰 **Video Poker** | Bet: ${bet}",
            "embeds": [{
                "description": f"Twoja ręka:\n# {cards_str}\n\nKliknij przyciski, aby zatrzymać karty (HOLD). Reszta zostanie wymieniona.",
                "color": 0x2b2d31
            }],
            "components": build_components([])
        }
    }

# --- OBSŁUGA KLIKNIĘĆ (INTERAKCJE) ---
def handle_poker_component(data):
    user_id = data["member"]["user"]["id"]
    custom_id = data["data"]["custom_id"]
    
    game = get_game_state(user_id)
    if not game:
        return {"type": 4, "data": {"content": "❌ Ta gra wygasła. Wpisz /poker aby zagrać nową.", "flags": 64}}

    # 1. KLIKNIĘCIE KARTY (HOLD)
    if custom_id.startswith("poker_hold_"):
        idx = int(custom_id.split("_")[-1])
        
        # Przełącz stan (dodaj/usuń z held)
        if idx in game["held"]:
            game["held"].remove(idx)
        else:
            game["held"].append(idx)
        
        set_game_state(user_id, game) # Aktualizuj bazę
        
        # Aktualizuj tylko przyciski (nie zmieniaj kart jeszcze)
        return {
            "type": 7, # Update Message
            "data": {
                "components": build_components(game["held"])
            }
        }

    # 2. KLIKNIĘCIE DRAW (FINAŁ)
    if custom_id == "poker_draw":
        hand = game["hand"]
        deck = game["deck"]
        held = game["held"]
        bet = game["bet"]

        # Wymiana kart
        new_hand = []
        for i in range(5):
            if i in held:
                new_hand.append(hand[i]) # Zostaw
            else:
                new_hand.append(deck.pop(0)) # Dobierz nową
        
        # Wynik
        name, mult, color = get_hand_result(new_hand)
        winnings = bet * mult
        
        if winnings > 0:
            update_balance(user_id, winnings)
            result_msg = f"**WYGRANA!** +${winnings}"
        else:
            result_msg = f"**PRZEGRANA** -${bet}"
            
        new_balance = get_balance(user_id)
        
        # Czyścimy bazę
        delete_game_state(user_id)

        # Finalny wygląd
        final_cards = " ".join([f"`{c['rank']}{c['suit']}`" for c in new_hand])
        
        return {
            "type": 7, # Update Message
            "data": {
                "embeds": [{
                    "title": name,
                    "description": f"Ostateczna ręka:\n# {final_cards}\n\n{result_msg}\nStan konta: **${new_balance}**",
                    "color": color
                }],
                "components": [] # Usuń przyciski
            }
        }