import os
import requests
import random
from flask import Flask, jsonify, request
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# ==========================================
#              MODULE IMPORTS
# ==========================================

# --- FUN (Zostały w folderze fun) ---
from commands.fun.hello import HELLO_DATA, cmd_hello
from commands.fun.cat import CAT_DATA, cmd_cat
from commands.fun.eightball import EIGHTBALL_DATA, cmd_eightball

# --- SOCIAL (Nowy folder social) ---
from commands.social.profile import PROFILE_DATA, cmd_profile
from commands.social.avatar import AVATAR_DATA, cmd_avatar
from commands.social.ship import SHIP_DATA, cmd_ship
from commands.social.marry import MARRY_DATA, DIVORCE_DATA, cmd_marry, cmd_divorce, handle_marry_component

# --- UTILITY (Nowy folder utility) ---
from commands.utility.ai import AI_DATA, cmd_ask
from commands.utility.poll import POLL_DATA, cmd_poll, handle_poll_component

# --- GAMES (Nowy folder games) ---
from commands.games.coinflip import COINFLIP_DATA, cmd_coinflip
from commands.games.slots import SLOTS_DATA, cmd_slots
from commands.games.roulette import ROULETTE_DATA, cmd_roulette
from commands.games.rps import RPS_DATA, cmd_rps
from commands.games.trivia import TRIVIA_DATA, cmd_trivia, handle_trivia_component
# Games with Buttons
from commands.games.poker import POKER_DATA, cmd_poker, handle_poker_component
from commands.games.blackjack import BLACKJACK_DATA, cmd_blackjack, handle_blackjack_component
from commands.games.duel import DUEL_DATA, cmd_duel, handle_duel_component

# --- ECONOMY & RPG (Bez zmian) ---
from commands.economy.money import BALANCE_DATA, cmd_balance, DAILY_DATA, cmd_daily
from commands.economy.pay import PAY_DATA, cmd_pay
from commands.economy.richlist import RICHLIST_DATA, cmd_richlist
from commands.economy.work import WORK_DATA, cmd_work
from commands.economy.shop import SHOP_DATA, cmd_shop, handle_shop_component
from commands.economy.rob import ROB_DATA, cmd_rob
from commands.economy.crypto import CRYPTO_DATA, cmd_crypto
# Usunięto titles.py (funkcje są w shop.py)

# --- LEVELS (Bez zmian) ---
from commands.levels.rank import RANK_DATA, cmd_rank, LEADERBOARD_XP_DATA, cmd_leaderboard_xp

# --- ADMIN & SYSTEM (Bez zmian) ---
from commands.root.synctest import SYNCTEST_DATA, cmd_synctest
from commands.admin.server import SERVER_DATA, cmd_server_info
from commands.admin.help import HELP_DATA, cmd_help
from commands.admin.moderation import CLEAR_DATA, cmd_clear, KICK_DATA, cmd_kick, BAN_DATA, cmd_ban

# --- DATABASE (XP SYSTEM) ---
from database import add_xp

app = Flask(__name__)

# ==========================================
#              CONFIGURATION
# ==========================================
PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
APP_ID = os.environ.get("DISCORD_APP_ID")

# ==========================================
#           COMMAND REGISTRY
# ==========================================
ALL_COMMANDS = [
    # Fun
    HELLO_DATA, CAT_DATA, EIGHTBALL_DATA,
    
    # Social
    PROFILE_DATA, AVATAR_DATA, SHIP_DATA, MARRY_DATA, DIVORCE_DATA,
    
    # Utility
    AI_DATA, POLL_DATA,
    
    # Games
    COINFLIP_DATA, SLOTS_DATA, ROULETTE_DATA, RPS_DATA, TRIVIA_DATA,
    POKER_DATA, BLACKJACK_DATA, DUEL_DATA,
    
    # Economy
    BALANCE_DATA, DAILY_DATA, PAY_DATA, RICHLIST_DATA,
    WORK_DATA, SHOP_DATA, ROB_DATA, CRYPTO_DATA,
    # Nowe moduły GTA:
    # CRIME_DATA, BUSINESS_DATA, BUY_BIZ_DATA, LAUNDER_DATA (Jeśli dodałeś GTA, odkomentuj)
    
    # Levels
    RANK_DATA, LEADERBOARD_XP_DATA,
    
    # System & Admin
    SYNCTEST_DATA, SERVER_DATA, HELP_DATA,
    CLEAR_DATA, KICK_DATA, BAN_DATA
]

# ==========================================
#           LOGIC HANDLERS
# ==========================================
COMMAND_HANDLERS = {
    # Fun
    "hello": cmd_hello, "cat": cmd_cat, "8ball": cmd_eightball,
    
    # Social
    "profile": cmd_profile, "avatar": cmd_avatar, "ship": cmd_ship, 
    "marry": cmd_marry, "divorce": cmd_divorce,
    
    # Utility
    "ask": cmd_ask, "poll": cmd_poll,
    
    # Games
    "coinflip": cmd_coinflip, "slots": cmd_slots, "roulette": cmd_roulette, 
    "rps": cmd_rps, "trivia": cmd_trivia,
    "poker": cmd_poker, "blackjack": cmd_blackjack, "duel": cmd_duel,
    
    # Economy
    "balance": cmd_balance, "daily": cmd_daily, "pay": cmd_pay, "richlist": cmd_richlist,
    "work": cmd_work, "shop": cmd_shop, "rob": cmd_rob, "crypto": cmd_crypto,
    
    # Levels
    "rank": cmd_rank, "leaderboard": cmd_leaderboard_xp,
    
    # System & Admin
    "synctest": cmd_synctest, "serverinfo": cmd_server_info, "help": cmd_help,
    "clear": cmd_clear, "kick": cmd_kick, "ban": cmd_ban
}

# ==========================================
#              ENDPOINTS
# ==========================================

@app.route('/', methods=['POST'])
def interactions():
    # 1. Security Verification
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except Exception:
        return "Invalid signature", 401

    r = request.json
    
    # 2. Handle PING
    if r["type"] == 1:
        return jsonify({"type": 1})
    
    # --- GLOBAL XP SYSTEM ---
    leveled_up = False
    new_lvl = 0
    
    if "member" in r:
        user_id = r["member"]["user"]["id"]
        xp_gain = random.randint(5, 15)
        new_lvl, leveled_up = add_xp(user_id, xp_gain)
    
    # 3. Handle SLASH COMMANDS
    if r["type"] == 2:
        name = r["data"]["name"]
        
        # Pass context
        if "guild_id" in r: r["data"]["guild_id"] = r["guild_id"]
        if "member" in r: r["data"]["member"] = r["member"]
        r["data"]["token"] = r.get("token")
        r["data"]["application_id"] = r.get("application_id")
        if "channel_id" in r: r["data"]["channel_id"] = r["channel_id"]
        if "data" in r and "resolved" in r["data"]:
             r["data"]["resolved"] = r["data"]["resolved"]

        if name in COMMAND_HANDLERS:
            response = COMMAND_HANDLERS[name](r["data"])
            
            # XP Notification
            if leveled_up and isinstance(response, dict) and "data" in response:
                msg = response["data"].get("content", "")
                prefix = "\n\n" if msg else ""
                response["data"]["content"] = f"{msg}{prefix}⭐ **LEVEL UP!** You reached **Level {new_lvl}**!"
            
            return jsonify(response)
            
        return jsonify({"error": "unknown command"}), 400
    
    # 4. Handle COMPONENTS
    if r["type"] == 3:
        custom_id = r["data"]["custom_id"]
        response = None
        
        # Router
        if custom_id.startswith("poker_"): response = handle_poker_component(r)
        elif custom_id.startswith("bj_"): response = handle_blackjack_component(r)
        elif custom_id.startswith("duel_"): response = handle_duel_component(r)
        elif custom_id.startswith("trivia_"): response = handle_trivia_component(r)
        elif custom_id.startswith("poll_"): response = handle_poll_component(r)
        elif custom_id.startswith("marry_"): response = handle_marry_component(r)
        elif custom_id == "shop_buy_select": response = handle_shop_component(r)
            
        if response:
            return jsonify(response)

    return jsonify({"error": "unknown interaction"}), 400

@app.route('/admin/refresh-commands', methods=['GET'])
def refresh_commands():
    if not APP_ID or not BOT_TOKEN:
        return "Missing configuration", 500
    url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    r = requests.put(url, headers=headers, json=ALL_COMMANDS)
    return f"Status: {r.status_code}<br>{r.text}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))