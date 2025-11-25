SHIP_DATA = {
    "name": "ship",
    "description": "Check love compatibility",
    "type": 1,
    "options": [
        {"name": "user1", "description": "First user", "type": 6, "required": True},
        {"name": "user2", "description": "Second user", "type": 6, "required": True}
    ]
}

def cmd_ship(data):
    user1_id = data["options"][0]["value"]
    user2_id = data["options"][1]["value"]
    
    # Matematyka miłości: (ID1 + ID2) % 101
    # Dzięki temu wynik jest stały dla tej samej pary!
    score = (int(user1_id) + int(user2_id)) % 101
    
    # Pasek postępu
    blocks = score // 10
    progress_bar = "💖" * blocks + "🖤" * (10 - blocks)
    
    # Komentarz
    if score == 100: text = "PERFECT MATCH! 💍"
    elif score > 80: text = "True Love! 🥰"
    elif score > 50: text = "Maybe... 🤔"
    else: text = "Run away! 🏃‍♂️"

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "💘 Love Calculator",
                "description": f"<@{user1_id}> + <@{user2_id}>\n\n**{score}%**\n{progress_bar}\n\n*{text}*",
                "color": 0xff69b4 # Hot Pink
            }]
        }
    }