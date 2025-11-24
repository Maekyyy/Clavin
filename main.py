import os
import requests
from flask import Flask, jsonify, request
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# === IMPORTUJEMY MODUŁY ===
from commands.fun.hello import HELLO_DATA, cmd_hello
from commands.root.synctest import SYNCTEST_DATA, cmd_synctest
from commands.admin.server import SERVER_DATA, cmd_server_info

app = Flask(__name__)

# --- KONFIGURACJA ---
PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
APP_ID = os.environ.get("DISCORD_APP_ID")  # <-- Twoje ID wpisane na sztywno

# --- REJESTR KOMEND ---
ALL_COMMANDS = [
    HELLO_DATA,
    SYNCTEST_DATA,
    SERVER_DATA
]

COMMAND_HANDLERS = {
    "hello": cmd_hello,
    "synctest": cmd_synctest,
    "serverinfo": cmd_server_info
}

# --- ENDPOINTY ---
@app.route('/', methods=['POST'])
def interactions():
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except Exception:
        return "Invalid signature", 401

    r = request.json
    if r["type"] == 1: return jsonify({"type": 1})
    
    if r["type"] == 2:
        name = r["data"]["name"]
        # Przekazujemy dodatkowe dane kontekstowe
        if "guild_id" in r: r["data"]["guild_id"] = r["guild_id"]
        if "member" in r: r["data"]["member"] = r["member"]

        if name in COMMAND_HANDLERS:
            return jsonify(COMMAND_HANDLERS[name](r["data"]))
            
    return jsonify({"error": "unknown command"}), 400

@app.route('/admin/refresh-commands', methods=['GET'])
def refresh_commands():
    url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    r = requests.put(url, headers=headers, json=ALL_COMMANDS)
    return f"Status: {r.status_code}<br>{r.text}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))