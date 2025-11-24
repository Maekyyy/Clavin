import random
from database import get_balance, update_balance, get_inventory, remove_item

ROB_DATA = {
    "name": "rob",
    "description": "Try to steal from another user",
    "type": 1,
    "options": [{
        "name": "victim",
        "description": "Who to rob?",
        "type": 6, # User
        "required": True
    }]
}

def cmd_rob(data):
    robber_id = data["member"]["user"]["id"]
    victim_id = data["options"][0]["value"]

    if robber_id == victim_id:
        return {"type": 4, "data": {"content": "❌ You can't rob yourself."}}

    victim_bal = get_balance(victim_id)
    if victim_bal < 100:
        return {"type": 4, "data": {"content": "❌ They are too poor to rob (min $100)."}}

    # SPRAWDŹ TARCZĘ
    victim_inv = get_inventory(victim_id)
    if "shield" in victim_inv:
        # Tarcza działa!
        remove_item(victim_id, "shield") # Tarcza pęka
        fine = 200 # Grzywna dla złodzieja
        update_balance(robber_id, -fine)
        
        return {
            "type": 4,
            "data": {
                "content": f"🛡️ **BLOCKED!** <@{victim_id}> used a **Shield**!\nYou got caught and paid **${fine}** fine."
            }
        }

    # SZANSA NA SUKCES (40%)
    if random.random() < 0.4:
        steal_percent = random.uniform(0.1, 0.5) # Ukradnij 10-50%
        stolen = int(victim_bal * steal_percent)
        
        update_balance(victim_id, -stolen)
        update_balance(robber_id, stolen)
        
        return {
            "type": 4,
            "data": {
                "content": f"🔫 **HEIST SUCCESSFUL!**\nYou stole **${stolen}** from <@{victim_id}>!"
            }
        }
    else:
        fine = 200
        update_balance(robber_id, -fine)
        return {
            "type": 4,
            "data": {
                "content": f"🚓 **POLICE!** You failed and paid **${fine}** fine."
            }
        }