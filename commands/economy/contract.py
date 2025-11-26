import random
from database import update_balance, check_cooldown, get_inventory

CONTRACT_DATA = {
    "name": "contract",
    "description": "Take a shady job for money",
    "type": 1
}

MISSIONS = [
    {"name": "Smuggle Goods", "req": None, "reward": 300, "risk": 0.2},
    {"name": "Hack Bank ATM", "req": "fake_id", "reward": 800, "risk": 0.4},
    {"name": "Heist at Casino", "req": "lockpick", "reward": 1500, "risk": 0.6},
]

def cmd_contract(data):
    user_id = data["member"]["user"]["id"]
    
    # Cooldown 2h
    ok, left = check_cooldown(user_id, "contract", 7200)
    if not ok: return {"type": 4, "data": {"content": f"⏳ Wait {int(left//60)} mins for new contracts."}}
    
    inv = get_inventory(user_id)
    mission = random.choice(MISSIONS)
    
    # Sprawdź wymagania
    req_item = mission['req']
    if req_item and req_item not in inv:
        return {"type": 4, "data": {"content": f"❌ **Mission Failed:** You need a **{req_item.upper()}** for '{mission['name']}'."}}
        
    # Ryzyko
    if random.random() > mission['risk']:
        update_balance(user_id, mission['reward'])
        return {"type": 4, "data": {"content": f"✅ **Success!** Completed '{mission['name']}' and earned **${mission['reward']}**."}}
    else:
        fine = int(mission['reward'] / 2)
        update_balance(user_id, -fine)
        return {"type": 4, "data": {"content": f"🚓 **Failed!** Police stopped '{mission['name']}'. Fined **${fine}**."}}