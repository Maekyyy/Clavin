# To jest zwykła funkcja, nie potrzebuje dekoratorów @bot.command
def cmd_hello(data):
    # Logika wyciągania argumentów
    options = data.get("options", [])
    user_name = "Nieznajomy"
    
    for option in options:
        if option["name"] == "name":
            user_name = option["value"]

    return {
        "type": 4,
        "data": {
            "content": f"👋 Cześć {user_name}! To odpowiedź z pliku general.py"
        }
    }

def cmd_synctest(data):
    return {
        "type": 4,
        "data": {
            "content": "✅ Połączenie działa! Struktura plików jest poprawna."
        }
    }