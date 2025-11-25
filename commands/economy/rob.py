import random
from database import get_balance, update_balance, get_inventory, remove_item

ROB_DATA = {
    "name": "rob",
    "description": "Try to steal from another user",
    "type": 1,
    "options": [{"name": "victim", "description": "Who to rob?", "type": 6, "required": True}]
}

def cmd_rob(data):
    robber_id = data["member"]["user"]["id"]
    victim_id = data["options"][0]["value"]

    if robber_id == victim_id: return {"type": 4, "data": {"content": "❌ You can't rob yourself."}}

    victim_bal = get_balance(victim_id)
    if victim_bal < 100: return {"type": 4, "data": {"content": "❌ They are too poor (min $100)."}}

    # --- SPRAWDZANIE EKWIPUNKU ---
    robber_inv = get_inventory(robber_id)
    victim_inv = get_inventory(victim_id)

    # 1. Tarcza ofiary (Shield)
    if "shield" in victim_inv:
        remove_item(victim_id, "shield")
        fine = 200
        # Jeśli złodziej ma Fake ID, płaci mniej
        if "fake_id" in robber_inv: fine = 100
            
        update_balance(robber_id, -fine)
        return {"type": 4, "data": {"content": f"🛡️ **BLOCKED!** Victim used a **Shield**!\nYou paid **${fine}** fine."}}

    # 2. Oblicz szansę (Lockpick)
    success_chance = 0.40 # Bazowa 40%
    if "lockpick" in robber_inv:
        success_chance = 0.55 # Z wytrychem 55%

    if random.random() < success_chance:
        # SUKCES
        steal_percent = random.uniform(0.1, 0.5)
        stolen = int(victim_bal * steal_percent)
        update_balance(victim_id, -stolen)
        update_balance(robber_id, stolen)
        
        bonus_msg = " (Using 🧷 Lockpick)" if "lockpick" in robber_inv else ""
        return {"type": 4, "data": {"content": f"🔫 **HEIST SUCCESSFUL!**{bonus_msg}\nYou stole **${stolen}** from <@{victim_id}>!"}}
    else:
        # PORAŻKA (Policja)
        fine = random.randint(200, 500)
        
        # Fake ID zmniejsza karę o połowę
        if "fake_id" in robber_inv:
            fine = int(fine / 2)
            msg = f"🚓 **BUSTED!** But your **🆔 Fake ID** worked!\nYou only paid **${fine}** bribe."
        else:
            msg = f"🚓 **BUSTED!** Police caught you.\nYou paid **${fine}** fine."
            
        update_balance(robber_id, -fine)
        return {"type": 4, "data": {"content": msg}}