import random

ROLL_DATA = {
    "name": "roll",
    "description": "Roll dice (e.g. 1d20, 2d6)",
    "type": 1,
    "options": [{
        "name": "dice",
        "description": "Format: XdY (e.g. 1d20, 2d6, 1d100)",
        "type": 3,
        "required": False
    }]
}

def cmd_roll(data):
    options = data.get("options", [])
    dice_str = "1d20" # Domyślnie rzut kością 20-ścienną
    
    if options:
        dice_str = options[0]["value"]
        
    try:
        # Parsowanie (np. "2d6" -> 2 rzuty, kość 6)
        if "d" not in dice_str:
            return {"type": 4, "data": {"content": "❌ Invalid format. Use `XdY` (e.g. `2d6`)."}}
            
        parts = dice_str.lower().split("d")
        count = int(parts[0]) if parts[0] else 1
        sides = int(parts[1])
        
        # Limity (żeby nie zawiesić bota)
        if count > 100 or sides > 1000000 or count < 1 or sides < 1:
             return {"type": 4, "data": {"content": "❌ Numbers too big/small! Max 100 dice."}}

        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        
        # Formatowanie wyniku
        if count == 1:
            desc = f"🎲 Result: **{total}**"
        else:
            rolls_str = ", ".join(map(str, rolls))
            if len(rolls_str) > 100: rolls_str = "..." # Ucinamy jak za długie
            desc = f"🎲 Results: [{rolls_str}]\n**Total: {total}**"

        return {
            "type": 4,
            "data": {
                "embeds": [{
                    "title": f"Rolling {dice_str}",
                    "description": desc,
                    "color": 0x9b59b6
                }]
            }
        }
        
    except ValueError:
        return {"type": 4, "data": {"content": "❌ Invalid number format. Use `XdY`."}}