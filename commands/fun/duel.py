import random
from database import get_balance, update_balance, set_game_state, get_game_state, delete_game_state

DUEL_DATA = {
    "name": "duel",
    "description": "Challenge someone to a coinflip duel",
    "type": 1,
    "options": [
        {"name": "opponent", "description": "Who to fight?", "type": 6, "required": True},
        {"name": "bet", "description": "Amount to bet", "type": 4, "required": True}
    ]
}

def cmd_duel(data):
    challenger_id = data["member"]["user"]["id"]
    opponent_id = data["options"][0]["value"]
    bet = data["options"][1]["value"]

    if challenger_id == opponent_id:
        return {"type": 4, "data": {"content": "❌ You cannot duel yourself."}}
    
    if bet < 1:
        return {"type": 4, "data": {"content": "❌ Invalid bet."}}

    # Sprawdź fundusze obu graczy
    if get_balance(challenger_id) < bet:
        return {"type": 4, "data": {"content": "❌ You don't have enough money!"}}
    
    if get_balance(opponent_id) < bet:
        return {"type": 4, "data": {"content": f"❌ <@{opponent_id}> is too poor for this duel."}}

    # Zapisz stan pod ID PRZECIWNIKA (bo on musi kliknąć)
    game_data = {
        "type": "duel",
        "challenger": challenger_id,
        "opponent": opponent_id,
        "bet": bet
    }
    # Używamy ID oponenta jako klucza, bo to on ma 'aktywną akcję' do wykonania
    if get_game_state(opponent_id):
        return {"type": 4, "data": {"content": "❌ Opponent is busy with another game."}}
        
    set_game_state(opponent_id, game_data)

    return {
        "type": 4,
        "data": {
            "content": f"⚔️ <@{opponent_id}>, you have been challenged by <@{challenger_id}> for **${bet}**!",
            "components": [{
                "type": 1,
                "components": [
                    {"type": 2, "style": 3, "label": "ACCEPT", "custom_id": "duel_accept"}, # Zielony
                    {"type": 2, "style": 4, "label": "DECLINE", "custom_id": "duel_decline"} # Czerwony
                ]
            }]
        }
    }

def handle_duel_component(data):
    clicker_id = data["member"]["user"]["id"]
    custom_id = data["data"]["custom_id"]
    
    # Pobieramy grę przypisaną do klikającego (to on jest Oponentem)
    game = get_game_state(clicker_id)
    
    if not game or game.get("type") != "duel":
        return {"type": 4, "data": {"content": "❌ Duel expired or invalid.", "flags": 64}}

    if custom_id == "duel_decline":
        delete_game_state(clicker_id)
        return {
            "type": 7,
            "data": {
                "content": "🛡️ Duel declined.",
                "components": []
            }
        }

    if custom_id == "duel_accept":
        # Ponowne sprawdzenie kasy (mogła zniknąć w międzyczasie)
        p1 = game["challenger"]
        p2 = game["opponent"]
        bet = game["bet"]
        
        if get_balance(p1) < bet or get_balance(p2) < bet:
             delete_game_state(clicker_id)
             return {"type": 7, "data": {"content": "❌ One of you ran out of money!", "components": []}}

        # Pobieramy kasę
        update_balance(p1, -bet)
        update_balance(p2, -bet)
        
        # Walczymy! (50/50)
        winner = random.choice([p1, p2])
        loser = p2 if winner == p1 else p1
        
        # Wypłata (Pula = 2 * bet)
        update_balance(winner, bet * 2)
        delete_game_state(clicker_id)
        
        return {
            "type": 7,
            "data": {
                "content": f"⚔️ **DUEL FINISHED!**\n\n🏆 Winner: <@{winner}> (Won **${bet}**)\n💀 Loser: <@{loser}>",
                "components": []
            }
        }