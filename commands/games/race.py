import random
import time
import requests
from threading import Thread
from database import get_balance, update_balance

RACE_DATA = {
    "name": "race",
    "description": "Bet on a horse race",
    "type": 1,
    "options": [
        {"name": "bet", "description": "Bet amount", "type": 4, "required": True},
        {"name": "horse", "description": "Choose horse (1-5)", "type": 4, "required": True, "min_value": 1, "max_value": 5}
    ]
}

def run_race(token, app_id, user_id, bet, chosen_horse):
    # Symulacja wyścigu (aktualizacja wiadomości)
    horses = [0] * 5 # Pozycje (0-20)
    track_len = 15
    winner = -1
    
    url = f"https://discord.com/api/v10/webhooks/{app_id}/{token}/messages/@original"
    
    # Pętla klatek animacji
    for _ in range(8): # Max 8 aktualizacji
        time.sleep(1.5)
        
        # Ruch koni
        for i in range(5):
            move = random.randint(1, 3)
            horses[i] += move
            if horses[i] >= track_len and winner == -1:
                winner = i + 1
        
        # Generowanie toru
        track = ""
        for i in range(5):
            pos = min(horses[i], track_len)
            line = "-" * pos + "🐎" + "-" * (track_len - pos)
            track += f"**{i+1}.** |{line}| {'🏁' if pos >= track_len else ''}\n"
            
        # Wyślij aktualizację
        requests.patch(url, json={"content": f"🏇 **RACE IN PROGRESS!**\n\n{track}"})
        
        if winner != -1: break
        
    # Koniec
    if winner == chosen_horse:
        winnings = bet * 4 # Wypłata x4 (bo 5 koni)
        update_balance(user_id, winnings)
        res_msg = f"🎉 **VICTORY!** Horse {winner} won! You got **${winnings}**!"
    else:
        res_msg = f"💀 **LOST.** Horse {winner} won."
        
    requests.patch(url, json={"content": f"🏁 **RACE FINISHED!**\n\n{track}\n{res_msg}"})


def cmd_race(data):
    user_id = data["member"]["user"]["id"]
    bet = data["options"][0]["value"]
    horse = data["options"][1]["value"]
    
    if get_balance(user_id) < bet: return {"type": 4, "data": {"content": "❌ Too poor."}}
    
    update_balance(user_id, -bet)
    
    # Start w tle
    token = data["token"]
    app_id = data["application_id"]
    t = Thread(target=run_race, args=(token, app_id, user_id, bet, horse))
    t.start()
    
    return {"type": 4, "data": {"content": "🔫 **The race is starting!** Watch closely..."}}