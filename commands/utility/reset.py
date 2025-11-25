from database import delete_game_state

RESET_DATA = {
    "name": "reset",
    "description": "Force quit current game (Fix stuck bot)",
    "type": 1
}

def cmd_reset(data):
    user_id = data["member"]["user"]["id"]
    
    # Siłowe usunięcie gry z bazy
    delete_game_state(user_id)
    
    return {
        "type": 4,
        "data": {
            "content": "✅ **Game state cleared!**\nYou can now start a new game."
        }
    }