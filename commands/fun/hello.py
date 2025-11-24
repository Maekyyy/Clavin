# DEFINICJA KOMENDY (Dla Discorda)
HELLO_DATA = {
    "name": "hello",
    "description": "Przywitaj się z botem (Module Fun)",
    "type": 1,
    "options": [{
        "name": "name",
        "description": "Twoje imię",
        "type": 3,
        "required": True
    }]
}

# LOGIKA KOMENDY
def cmd_hello(data):
    options = data.get("options", [])
    user_name = "Nieznajomy"
    for option in options:
        if option["name"] == "name":
            user_name = option["value"]
            
    return {
        "type": 4,
        "data": {
            "content": f"👋 Cześć {user_name}! Pozdrowienia z folderu **fun**!"
        }
    }