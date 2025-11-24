import os
import requests # Musisz to dodać do requirements.txt jeśli nie ma!
from flask import Flask, jsonify, request
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from commands.general import cmd_hello, cmd_synctest

app = Flask(__name__)

# --- KONFIGURACJA ---
PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
# APP_ID musimy wyciągnąć z tokena lub wpisać ręcznie. 
# Dla uproszczenia wpisz tu swoje ID Aplikacji:
APP_ID = "1212759038643802182" 

# --- LISTA KOMEND (TU JE DEFINIUJESZ RAZ) ---
# To jest Twoja "baza" komend. Jak chcesz dodać nową, dopisujesz ją tutaj.
ALL_COMMANDS = [
    {
        "name": "hello",
        "description": "Przywitaj się z botem (Cloud Run)",
        "type": 1,
        "options": [{
            "name": "name",
            "description": "Twoje imię",
            "type": 3,
            "required": True
        }]
    },
    {
        "name": "synctest",
        "description": "Test połączenia",
        "type": 1
    }
]

# --- OBSŁUGA LOGIKI ---
COMMAND_HANDLERS = {
    "hello": cmd_hello,
    "synctest": cmd_synctest,
}

# --- ENDPOINT 1: INTERAKCJE DISCORDA ---
@app.route('/', methods=['POST'])
def interactions():
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except (BadSignatureError, Exception):
        return "Invalid signature", 401

    r = request.json
    if r["type"] == 1: return jsonify({"type": 1})
    if r["type"] == 2:
        name = r["data"]["name"]
        if name in COMMAND_HANDLERS:
            return jsonify(COMMAND_HANDLERS[name](r["data"]))
    return jsonify({"error": "unknown command"}), 400

# --- ENDPOINT 2: MAGICZNY LINK (NOWOŚĆ!) ---
# Wchodzisz na: https://twoj-bot.run.app/admin/refresh-commands
@app.route('/admin/refresh-commands', methods=['GET'])
def refresh_commands():
    if not BOT_TOKEN or not APP_ID:
        return "Brak konfiguracji (Token/App ID)", 500
        
    url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    
    # Bot sam wysyła listę ALL_COMMANDS do Discorda
    r = requests.put(url, headers=headers, json=ALL_COMMANDS)
    
    if r.status_code in [200, 201]:
        return f"✅ Sukces! Zarejestrowano {len(ALL_COMMANDS)} komend.<br>Odpowiedź API: {r.status_code}"
    else:
        return f"❌ Błąd: {r.status_code}<br>{r.text}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))