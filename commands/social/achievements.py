from database import get_balance, get_inventory, get_businesses, get_title, get_level_data, get_achievements, unlock_achievement

ACHIEVEMENTS_DEF = {
    # COMMON
    "novice": {"name": "🌱 Novice", "desc": "Reach Level 2", "xp_reward": 50},
    "worker": {"name": "👷 Hard Worker", "desc": "Earn $5,000 Cash", "xp_reward": 100},
    
    # RARE
    "criminal": {"name": "🔫 Criminal", "desc": "Own a Weed Farm & Fake ID", "xp_reward": 300},
    "armed": {"name": "🛡️ Armed & Dangerous", "desc": "Own Shield & Lockpick", "xp_reward": 300},
    "investor": {"name": "📈 Investor", "desc": "Own 3 different businesses", "xp_reward": 500},
    
    # LEGENDARY / SECRET
    "tycoon": {"name": "🏭 Cartel Boss", "desc": "Own a Nightclub", "xp_reward": 1000},
    "millionaire": {"name": "💎 Millionaire", "desc": "Have $1,000,000", "xp_reward": 5000},
    "royal": {"name": "👑 Royalty", "desc": "Purchase the 'King' title", "xp_reward": 2000}
}

ACHIEVEMENTS_DATA = {
    "name": "achievements",
    "description": "Check your unlocked badges",
    "type": 1
}

def check_new_unlocks(user_id):
    """Sprawdza warunki i przyznaje nowe odznaki."""
    unlocked_now = []
    current_badges = get_achievements(user_id)
    
    # Pobierz wszystkie dane
    cash = get_balance(user_id)
    inv = get_inventory(user_id)
    biz = get_businesses(user_id)
    title = get_title(user_id)
    level, _ = get_level_data(user_id)
    
    # --- LOGIKA SPRAWDZANIA ---
    
    # 1. Novice (Level 2)
    if "novice" not in current_badges and level >= 2:
        unlock_achievement(user_id, "novice")
        unlocked_now.append("novice")
        
    # 2. Hard Worker ($5000)
    if "worker" not in current_badges and cash >= 5000:
        unlock_achievement(user_id, "worker")
        unlocked_now.append("worker")
        
    # 3. Criminal (Weed + ID)
    if "criminal" not in current_badges and "weed" in biz and "fake_id" in inv:
        unlock_achievement(user_id, "criminal")
        unlocked_now.append("criminal")
        
    # 4. Armed (Shield + Lockpick)
    if "armed" not in current_badges and "shield" in inv and "lockpick" in inv:
        unlock_achievement(user_id, "armed")
        unlocked_now.append("armed")
        
    # 5. Investor (3 different biz)
    if "investor" not in current_badges and len(biz.keys()) >= 3:
        unlock_achievement(user_id, "investor")
        unlocked_now.append("investor")
        
    # 6. Cartel Boss (Nightclub)
    if "tycoon" not in current_badges and "nightclub" in biz:
        unlock_achievement(user_id, "tycoon")
        unlocked_now.append("tycoon")
        
    # 7. Millionaire ($1M)
    if "millionaire" not in current_badges and cash >= 1000000:
        unlock_achievement(user_id, "millionaire")
        unlocked_now.append("millionaire")
        
    # 8. Royalty (King Title)
    if "royal" not in current_badges and title == "King":
        unlock_achievement(user_id, "royal")
        unlocked_now.append("royal")
        
    return unlocked_now

def cmd_achievements(data):
    user_id = data["member"]["user"]["id"]
    username = data["member"]["user"]["username"]
    
    # Najpierw sprawdź, czy coś się odblokowało w tym momencie
    new_unlocks = check_new_unlocks(user_id)
    
    # Pobierz aktualną listę
    my_badges = get_achievements(user_id)
    
    desc = ""
    if new_unlocks:
        desc += f"🎉 **NEW UNLOCKS:** {', '.join([ACHIEVEMENTS_DEF[u]['name'] for u in new_unlocks])}\n\n"
    
    desc += "__**Your Collection:**__\n"
    
    if not my_badges:
        desc += "*No achievements yet. Start playing to unlock!*"
    else:
        for bid in my_badges:
            if bid in ACHIEVEMENTS_DEF:
                badge = ACHIEVEMENTS_DEF[bid]
                desc += f"{badge['name']} - *{badge['desc']}*\n"
                
    # Pokaż ile brakuje
    total = len(ACHIEVEMENTS_DEF)
    owned = len(my_badges)
    progress = int((owned / total) * 100)
    bar = "🟩" * (progress // 10) + "⬛" * (10 - (progress // 10))
    
    desc += f"\n**Progress:** {bar} {progress}% ({owned}/{total})"

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": f"🏆 Achievements: {username}",
                "description": desc,
                "color": 0xffd700 # Gold
            }]
        }
    }