import random
from database import get_balance, update_balance, set_game_state, get_game_state, delete_game_state

TTT_DATA = {
    "name": "tictactoe",
    "description": "Play Tic Tac Toe against a friend",
    "type": 1,
    "options": [
        {"name": "opponent", "description": "Opponent", "type": 6, "required": True},
        {"name": "bet", "description": "Bet amount", "type": 4, "required": True}
    ]
}

def check_winner(board):
    # Wygrane kombinacje
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] and board[a] != 0:
            return board[a] # Zwraca ID gracza (1 lub 2)
    if 0 not in board: return "draw"
    return None

def get_ttt_buttons(board):
    buttons = []
    # Zamień 0->Szary, 1->X(Blurple), 2->O(Red)
    for i, val in enumerate(board):
        style = 2
        label = "\u200b" # Pusty znak
        disabled = False
        
        if val == 1:
            style = 1 # Blurple
            label = "X"
            disabled = True
        elif val == 2:
            style = 4 # Red
            label = "O"
            disabled = True
            
        buttons.append({
            "type": 2, "style": style, "label": label,
            "custom_id": f"ttt_{i}", "disabled": disabled
        })
    
    # Podział na rzędy 3x3
    rows = []
    for i in range(0, 9, 3):
        rows.append({"type": 1, "components": buttons[i:i+3]})
    return rows

def cmd_tictactoe(data):
    p1 = data["member"]["user"]["id"]
    p2 = data["options"][0]["value"]
    bet = data["options"][1]["value"]

    if p1 == p2: return {"type": 4, "data": {"content": "❌ Play with someone else."}}
    if bet < 1: return {"type": 4, "data": {"content": "❌ Invalid bet."}}
    
    if get_balance(p1) < bet: return {"type": 4, "data": {"content": "❌ You are broke."}}
    if get_balance(p2) < bet: return {"type": 4, "data": {"content": f"❌ <@{p2}> is broke."}}

    if get_game_state(p2): return {"type": 4, "data": {"content": "❌ Opponent is busy."}}

    # Zapisz stan (Zapisujemy pod ID obu graczy, żeby wiedzieli że grają)
    # Ale główny stan trzymamy pod ID Playera 1 (challenger)
    # Tutaj uproszczona wersja: startuje od razu (bez akceptacji dla szybkości, albo z?)
    # Zróbmy z akceptacją jak w Duelu, ale tu od razu gra:
    
    update_balance(p1, -bet)
    update_balance(p2, -bet)

    game_data = {
        "type": "tictactoe",
        "p1": p1, "p2": p2, "bet": bet,
        "turn": p1, # P1 zaczyna
        "board": [0]*9
    }
    set_game_state(p1, game_data) # P1 jest "hostem" gry
    
    # Hack: Zapisz też u P2, żeby wiedział gdzie szukać (pointer)
    set_game_state(p2, {"type": "ttt_pointer", "host": p1})

    return {
        "type": 4,
        "data": {
            "content": f"❌⭕ **Tic Tac Toe**\n<@{p1}> vs <@{p2}>\nBet: ${bet}\n\nTarget: **<@{p1}>'s Turn (X)**",
            "components": get_ttt_buttons([0]*9)
        }
    }

def handle_ttt_component(data):
    clicker = data["member"]["user"]["id"]
    custom_id = data["data"]["custom_id"]
    idx = int(custom_id.split("_")[1])
    
    # Znajdź grę
    state = get_game_state(clicker)
    if not state: return {"type": 4, "data": {"content": "❌ Game over.", "flags": 64}}
    
    host_id = state.get("host", clicker) # Jeśli to pointer, weź hosta
    game = get_game_state(host_id)
    
    if not game or game["type"] != "tictactoe":
         return {"type": 4, "data": {"content": "❌ Game error.", "flags": 64}}

    if clicker != game["turn"]:
        return {"type": 4, "data": {"content": "⏳ Not your turn!", "flags": 64}}

    # Ruch
    mark = 1 if clicker == game["p1"] else 2
    game["board"][idx] = mark
    
    # Sprawdź wynik
    winner = check_winner(game["board"])
    
    if winner:
        delete_game_state(game["p1"])
        delete_game_state(game["p2"])
        
        if winner == "draw":
            update_balance(game["p1"], game["bet"])
            update_balance(game["p2"], game["bet"])
            msg = "🤝 **DRAW!** Money returned."
            color = 0xf1c40f
        else:
            win_id = game["p1"] if winner == 1 else game["p2"]
            update_balance(win_id, game["bet"] * 2)
            msg = f"🏆 **WINNER:** <@{win_id}> (+${game['bet']})"
            color = 0x2ecc71
            
        return {
            "type": 7,
            "data": {
                "embeds": [{"description": msg, "color": color}],
                "components": get_ttt_buttons(game["board"]) # Pokaż planszę końcową
            }
        }
    
    # Zmiana tury
    game["turn"] = game["p2"] if clicker == game["p1"] else game["p1"]
    set_game_state(host_id, game)
    
    turn_msg = f"<@{game['turn']}>'s Turn ({'O' if mark==1 else 'X'})"
    
    return {
        "type": 7,
        "data": {
            "content": f"❌⭕ **Tic Tac Toe**\nBet: ${game['bet']}\n\nTarget: **{turn_msg}**",
            "components": get_ttt_buttons(game["board"])
        }
    }