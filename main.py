import os
import requests
from flask import Flask, jsonify, request
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# === IMPORTY MODUŁÓW ===
# Fun
from commands.fun.hello import HELLO_DATA, cmd_hello
from commands.fun.poker import POKER_DATA, cmd_poker, handle_poker_component
from commands.fun.cat import CAT_DATA, cmd_cat
from commands.fun.roulette import ROULETTE_DATA, cmd_roulette
from commands.fun.slots import SLOTS_DATA, cmd_slots
from commands.fun.eightball import EIGHTBALL_DATA, cmd_eightball
from commands.fun.coinflip import COINFLIP_DATA, cmd_coinflip

# Root & Admin
from commands.root.synctest import SYNCTEST_DATA, cmd_synctest
from commands.admin.server import SERVER_DATA, cmd_server_info
from commands.admin.help import HELP_DATA, cmd_help

# Economy
from commands.economy.money import BALANCE_DATA, cmd_balance, DAILY_DATA, cmd_daily
from commands.economy.richlist import RICHLIST_DATA, cmd_richlist
from commands.economy.pay import PAY_DATA, cmd_pay
from commands.economy.work import WORK_DATA, cmd_work
from commands.economy.shop import SHOP_DATA, cmd_shop
from commands.economy.rob import ROB_DATA, cmd_rob

app = Flask(__name__)

# --- KONFIGURACJA ---
# Pobieramy zmienne środowiskowe z Google Cloud Run
PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
APP_ID = os.environ.get("DISCORD_APP_ID")

# --- REJESTR KOMEND (Lista Definicji) ---
# To jest lista, którą wysyłamy do Discorda przez Magiczny Link
ALL_COMMANDS = [
    HELLO_DATA,
    SYNCTEST_DATA,
    SERVER_DATA,
    HELP_DATA,
    
    # Economy
    BALANCE_DATA,
    DAILY_DATA,
    RICHLIST_DATA,
    PAY_DATA,
    WORK_DATA,
    SHOP_DATA,
    ROB_DATA,
    
    # Fun / Games
    POKER_DATA,
    CAT_DATA,
    ROULETTE_DATA,
    SLOTS_DATA,
    EIGHTBALL_DATA,
    COINFLIP_DATA
]

# --- MAPA FUNKCJI (Logika) ---
# To łączy nazwę komendy (od Discorda) z funkcją w Pythonie
COMMAND_HANDLERS = {
    "hello": cmd_hello,
    "synctest": cmd_synctest,
    "serverinfo": cmd_server_info,
    "help": cmd_help,
    
    # Economy
    "balance": cmd_balance,
    "daily": cmd_daily,
    "richlist": cmd_richlist,
    "pay": cmd_pay,
    "work": cmd_work,
    "shop": cmd_shop,
    "rob": cmd_rob,
    
    # Fun / Games
    "poker": cmd_poker,
    "cat": cmd_cat,
    "roulette": cmd_roulette,
    "slots": cmd_slots,
    "8ball": cmd_eightball,
    "coinflip": cmd_coinflip
}

# --- ENDPOINTY ---

@app.route('/', methods=['POST'])
def interactions():
    # 1. Weryfikacja bezpieczeństwa (Ed25519)
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except Exception:
        return "Invalid signature", 401

    r = request.json
    
    # 2. Obsługa PING (Wymagane przez Discord)
    if r["type"] == 1:
        return jsonify({"type": 1})
    
    # 3. Obsługa SLASH COMMANDS (Wpisanie komendy)
    if r["type"] == 2:
        name = r["data"]["name"]
        
        # Przekazujemy dodatkowe dane kontekstowe (np. ID serwera, dane usera)
        if "guild_id" in r: r["data"]["guild_id"] = r["guild_id"]
        if "member" in r: r["data"]["member"] = r["member"]

        if name in COMMAND_HANDLERS:
            # Uruchamiamy odpowiednią funkcję i zwracamy jej wynik JSON
            return jsonify(COMMAND_HANDLERS[name](r["data"]))
            
        return jsonify({"error": "unknown command"}), 400
    
    # 4. Obsługa KOMPONENTÓW (Kliknięcie przycisku)
    if r["type"] == 3:
        custom_id = r["data"]["custom_id"]
        
        # Jeśli ID przycisku zaczyna się od "poker_", to sprawa dla pokera
        if custom_id.startswith("poker_"):
            return jsonify(handle_poker_component(r))

    return jsonify({"error": "unknown interaction"}), 400

# --- MAGICZNY LINK (Aktualizacja komend) ---
@app.route('/admin/refresh-commands', methods=['GET'])
def refresh_commands():
    if not APP_ID or not BOT_TOKEN:
        return "Brak konfiguracji (APP_ID lub BOT_TOKEN).", 500
        
    url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    
    # Wysyłamy całą listę ALL_COMMANDS do API Discorda
    r = requests.put(url, headers=headers, json=ALL_COMMANDS)
    
    if r.status_code in [200, 201]:
        return f"✅ Success! Updated {len(ALL_COMMANDS)} commands.<br>API Response: {r.status_code}"
    else:
        return f"❌ Error: {r.status_code}<br>{r.text}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))