# COMMAND DEFINITION (For Discord)
HELLO_DATA = {
    "name": "hello",
    "description": "Say hello to the bot (Fun Module)",
    "type": 1,
    "options": [{
        "name": "name",
        "description": "Your name",
        "type": 3,
        "required": True
    }]
}

# COMMAND LOGIC
def cmd_hello(data):
    options = data.get("options", [])
    user_name = "Stranger"
    for option in options:
        if option["name"] == "name":
            user_name = option["value"]
            
    return {
        "type": 4,
        "data": {
            "content": f"👋 Hello {user_name}! I'm all yours!"
        }
    }