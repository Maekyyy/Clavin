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
from commands.fun.avatar import AVATAR_DATA, cmd_avatar
from commands.fun.ship import SHIP_DATA, cmd_ship

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
from commands.economy.titles import BUY_TITLE_DATA, cmd_buy_title
from commands.economy.crypto import CRYPTO_DATA, cmd_crypto

# Levels
from commands.levels.rank import RANK_DATA, cmd_rank, LEADERBOARD_XP_DATA, cmd_leaderboard_xp

# Handlery interakcji gier (przyciski)
from commands.fun.blackjack import BLACKJACK_DATA, cmd_blackjack, handle_blackjack_component
from commands.fun.duel import DUEL_DATA, cmd_duel, handle_duel_component

# Baza danych (do XP)
from database import add_xp

app = Flask(__name__)

# --- KONFIGURACJA ---
PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
APP_ID = os.environ.get("DISCORD_APP_ID")

# --- REJESTR KOMEND (Lista Definicji) ---
ALL_COMMANDS = [
    # Fun
    HELLO_DATA, POKER_DATA, CAT_DATA, ROULETTE_DATA, SLOTS_DATA, 
    EIGHTBALL_DATA, COINFLIP_DATA, AVATAR_DATA, SHIP_DATA, 
    BLACKJACK_DATA, DUEL_DATA,
    
    # Admin/System
    SYNCTEST_DATA, SERVER_DATA, HELP_DATA,
    
    # Economy
    BALANCE_DATA, DAILY_DATA, RICHLIST_DATA, PAY_DATA, 
    WORK_DATA, SHOP_DATA, ROB_DATA, BUY_TITLE_DATA, CRYPTO_DATA,
    
    # Levels
    RANK_DATA, LEADERBOARD_XP_DATA
]

# --- MAPA FUNKCJI (Logika) ---
COMMAND_HANDLERS = {
    # Fun
    "hello": cmd_hello,
    "poker": cmd_poker,
    "cat": cmd_cat,
    "roulette": cmd_roulette,
    "slots": cmd_slots,
    "8ball": cmd_eightball,
    "coinflip": cmd_coinflip,
    "avatar": cmd_avatar,
    "ship": cmd_ship,
    "blackjack": cmd_blackjack,
    "duel": cmd_duel,
    
    # Admin/System
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
    "buy_title": cmd_buy_title,
    "crypto": cmd_crypto,
    
    # Levels
    "rank": cmd_rank,
    "leaderboard": cmd_leaderboard_xp
}

# --- ENDPOINTY ---

@app.route('/', methods=['POST'])
def interactions():
    # 1. Weryfikacja bezpieczeństwa
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except Exception:
        return "Invalid signature", 401

    r = request.json
    
    # 2. PING
    if r["type"] == 1:
        return jsonify({"type": 1})
    
    # --- SYSTEM XP (Globalny dla każdej akcji) ---
    # Każda interakcja (komenda lub przycisk) daje XP
    leveled_up = False
    new_lvl = 0
    
    if "member" in r:
        user_id = r["member"]["user"]["id"]
        # Losowe XP (5-15)
        import random
        xp_gain = random.randint(5, 15)
        new_lvl, leveled_up = add_xp(user_id, xp_gain)
    
    # 3. SLASH COMMANDS
    if r["type"] == 2:
        name = r["data"]["name"]
        
        # Przekazujemy dodatkowe dane
        if "guild_id" in r: r["data"]["guild_id"] = r["guild_id"]
        if "member" in r: r["data"]["member"] = r["member"]
        if "data" in r and "resolved" in r["data"]:
             r["data"]["resolved"] = r["data"]["resolved"]

        if name in COMMAND_HANDLERS:
            response = COMMAND_HANDLERS[name](r["data"])
            
            # Jeśli user awansował, dopisujemy gratulacje do wiadomości
            if leveled_up and isinstance(response, dict) and "data" in response:
                msg = response["data"].get("content", "")
                # Jeśli wiadomość ma treść, dodaj nową linię. Jeśli nie, stwórz treść.
                prefix = "\n\n" if msg else ""
                response["data"]["content"] = f"{msg}{prefix}⭐ **LEVEL UP!** You reached **Level {new_lvl}**!"
            
            return jsonify(response)
            
        return jsonify({"error": "unknown command"}), 400
    
    # 4. COMPONENT INTERACTION (Przyciski)
    if r["type"] == 3:
        custom_id = r["data"]["custom_id"]
        
        response = None
        if custom_id.startswith("poker_"):
            response = handle_poker_component(r)
        elif custom_id.startswith("bj_"):
            response = handle_blackjack_component(r)
        elif custom_id.startswith("duel_"):
            response = handle_duel_component(r)
            
        if response:
            # Tu też możemy dodać info o level up, jeśli przycisk kończy grę
            # Ale dla czystości interfejsu gier, lepiej to zostawić tylko przy komendach.
            return jsonify(response)

    return jsonify({"error": "unknown interaction"}), 400

# --- MAGICZNY LINK ---
@app.route('/admin/refresh-commands', methods=['GET'])
def refresh_commands():
    if not APP_ID or not BOT_TOKEN:
        return "Brak konfiguracji (APP_ID lub BOT_TOKEN).", 500
        
    url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    
    r = requests.put(url, headers=headers, json=ALL_COMMANDS)
    
    if r.status_code in [200, 201]:
        return f"✅ Success! Updated {len(ALL_COMMANDS)} commands.<br>API Response: {r.status_code}"
    else:
        return f"❌ Error: {r.status_code}<br>{r.text}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))