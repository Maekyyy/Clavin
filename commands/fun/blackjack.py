import random
from database import get_balance, update_balance, set_game_state, get_game_state, delete_game_state

BLACKJACK_DATA = {
    "name": "blackjack",
    "description": "Play Blackjack against the dealer",
    "type": 1,
    "options": [{
        "name": "bet",
        "description": "Amount to bet",
        "type": 4,
        "required": True
    }]
}

SUITS = ["♠️", "♥️", "♦️", "♣️"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

def get_deck():
    deck = [{'rank': r, 'suit': s} for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

def calculate_score(hand):
    score = 0
    aces = 0
    for card in hand:
        rank = card['rank']
        if rank in ["J", "Q", "K"]:
            score += 10
        elif rank == "A":
            aces += 1
            score += 11
        else:
            score += int(rank)
    
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return score

def format_hand(hand, hide_second=False):
    if hide_second:
        return f"`{hand[0]['rank']}{hand[0]['suit']}` `??`"
    return " ".join([f"`{c['rank']}{c['suit']}`" for c in hand])

# --- START GRY ---
def cmd_blackjack(data):
    user_id = data["member"]["user"]["id"]
    bet = data["options"][0]["value"]

    if get_game_state(user_id):
        return {"type": 4, "data": {"content": "❌ Finish your current game first!"}}
    
    if get_balance(user_id) < bet:
        return {"type": 4, "data": {"content": "❌ Not enough money."}}
    
    if bet < 1:
        return {"type": 4, "data": {"content": "❌ Bet positive amount."}}

    update_balance(user_id, -bet)

    deck = get_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    game_data = {
        "type": "blackjack",
        "bet": bet,
        "deck": deck,
        "player_hand": player_hand,
        "dealer_hand": dealer_hand
    }
    set_game_state(user_id, game_data)

    player_score = calculate_score(player_hand)
    
    # Sprawdź natychmiastowego Blackjacka
    if player_score == 21:
        return handle_blackjack_end(user_id, game_data, "blackjack")

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "🃏 Blackjack",
                "description": f"**Your Hand:** {calculate_score(player_hand)}\n{format_hand(player_hand)}\n\n**Dealer's Hand:**\n{format_hand(dealer_hand, hide_second=True)}",
                "color": 0x3498db
            }],
            "components": [{
                "type": 1,
                "components": [
                    {"type": 2, "style": 1, "label": "Hit", "custom_id": "bj_hit"},
                    {"type": 2, "style": 2, "label": "Stand", "custom_id": "bj_stand"}
                ]
            }]
        }
    }

# --- OBSŁUGA PRZYCISKÓW ---
def handle_blackjack_component(data):
    user_id = data["member"]["user"]["id"]
    custom_id = data["data"]["custom_id"]
    game = get_game_state(user_id)

    if not game or game.get("type") != "blackjack":
        return {"type": 4, "data": {"content": "❌ Game expired.", "flags": 64}}

    deck = game["deck"]
    player_hand = game["player_hand"]
    dealer_hand = game["dealer_hand"]

    if custom_id == "bj_hit":
        player_hand.append(deck.pop())
        score = calculate_score(player_hand)
        
        if score > 21:
            return handle_blackjack_end(user_id, game, "bust")
        
        game["player_hand"] = player_hand
        game["deck"] = deck
        set_game_state(user_id, game)
        
        return {
            "type": 7,
            "data": {
                "embeds": [{
                    "title": "🃏 Blackjack",
                    "description": f"**Your Hand:** {score}\n{format_hand(player_hand)}\n\n**Dealer's Hand:**\n{format_hand(dealer_hand, hide_second=True)}",
                    "color": 0x3498db
                }],
                "components": data["message"]["components"]
            }
        }

    if custom_id == "bj_stand":
        # Ruch krupiera (dobiera do 17)
        while calculate_score(dealer_hand) < 17:
            dealer_hand.append(deck.pop())
        
        game["dealer_hand"] = dealer_hand
        return handle_blackjack_end(user_id, game, "stand")

def handle_blackjack_end(user_id, game, reason):
    player_score = calculate_score(game["player_hand"])
    dealer_score = calculate_score(game["dealer_hand"])
    bet = game["bet"]
    
    winnings = 0
    result = ""
    color = 0x2b2d31

    if reason == "blackjack":
        winnings = int(bet * 2.5)
        result = "**BLACKJACK!**"
        color = 0xf1c40f
    elif reason == "bust":
        result = "**BUST!** (You went over 21)"
        color = 0xe74c3c
    else:
        # Porównanie wyników
        if dealer_score > 21:
            winnings = bet * 2
            result = "**DEALER BUST!** You win!"
            color = 0x2ecc71
        elif player_score > dealer_score:
            winnings = bet * 2
            result = "**YOU WIN!**"
            color = 0x2ecc71
        elif player_score == dealer_score:
            winnings = bet
            result = "**PUSH** (Tie)"
            color = 0x95a5a6
        else:
            result = "**DEALER WINS!**"
            color = 0xe74c3c

    if winnings > 0:
        update_balance(user_id, winnings)
        
    delete_game_state(user_id)
    
    return {
        "type": 7 if reason != "blackjack" else 4,
        "data": {
            "embeds": [{
                "title": f"🃏 Result: {result}",
                "description": f"**Your Hand:** {player_score}\n{format_hand(game['player_hand'])}\n\n**Dealer's Hand:** {dealer_score}\n{format_hand(game['dealer_hand'])}\n\nPayout: **${winnings}**",
                "color": color
            }],
            "components": []
        }
    }