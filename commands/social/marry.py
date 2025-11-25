from database import get_balance, update_balance, set_game_state, get_game_state, delete_game_state, set_marriage, get_partner, divorce_users

MARRY_DATA = {
    "name": "marry",
    "description": "Propose to someone!",
    "type": 1,
    "options": [{"name": "user", "description": "Your soulmate", "type": 6, "required": True}]
}

DIVORCE_DATA = {
    "name": "divorce",
    "description": "End your marriage ($5,000 fee)",
    "type": 1
}

def cmd_marry(data):
    proposer_id = data["member"]["user"]["id"]
    target_id = data["options"][0]["value"]
    
    if proposer_id == target_id: return {"type": 4, "data": {"content": "❌ Narcissism is not allowed."}}
    
    # Sprawdź czy już nie są po ślubie
    if get_partner(proposer_id): return {"type": 4, "data": {"content": "❌ You are already married!"}}
    if get_partner(target_id): return {"type": 4, "data": {"content": "❌ They are already married!"}}
    
    # Zapisz propozycję
    set_game_state(target_id, {
        "type": "marriage_proposal",
        "proposer": proposer_id
    })
    
    return {
        "type": 4,
        "data": {
            "content": f"💍 <@{target_id}>, **<@{proposer_id}> has proposed to you!**\nDo you accept?",
            "components": [{
                "type": 1,
                "components": [
                    {"type": 2, "style": 3, "label": "I DO! 💖", "custom_id": "marry_yes"},
                    {"type": 2, "style": 4, "label": "No way 🏃‍♂️", "custom_id": "marry_no"}
                ]
            }]
        }
    }

def handle_marry_component(data):
    target_id = data["member"]["user"]["id"]
    custom_id = data["data"]["custom_id"]
    
    game = get_game_state(target_id)
    if not game or game.get("type") != "marriage_proposal":
        return {"type": 4, "data": {"content": "❌ Proposal expired.", "flags": 64}}
        
    proposer_id = game["proposer"]
    delete_game_state(target_id)
    
    if custom_id == "marry_yes":
        set_marriage(proposer_id, target_id)
        return {
            "type": 7,
            "data": {
                "content": f"💒 **JUST MARRIED!** 💒\nCongratulations <@{proposer_id}> and <@{target_id}>!",
                "components": []
            }
        }
    else:
        return {"type": 7, "data": {"content": "💔 Proposal rejected.", "components": []}}

def cmd_divorce(data):
    user_id = data["member"]["user"]["id"]
    partner_id = get_partner(user_id)
    
    if not partner_id: return {"type": 4, "data": {"content": "❌ You are single."}}
    
    fee = 5000
    if get_balance(user_id) < fee:
        return {"type": 4, "data": {"content": f"❌ Lawyers cost money! You need **${fee}** to divorce."}}
        
    update_balance(user_id, -fee)
    divorce_users(user_id, partner_id)
    
    return {"type": 4, "data": {"content": f"💔 **Divorced.** You left <@{partner_id}>. Cost: ${fee}."}}