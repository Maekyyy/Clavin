import random
from database import get_balance, update_balance, get_businesses, buy_business_db, launder_money_db, check_cooldown

# --- KONFIGURACJA BIZNESÓW ---
BUSINESSES = {
    "corner": {
        "name": "🚬 Street Corner",
        "price": 2500,
        "income": 100, # $/h
        "desc": "Selling loose cigarettes."
    },
    "weed": {
        "name": "🌿 Weed Farm",
        "price": 15000,
        "income": 800, # $/h
        "desc": "Organic growth operation."
    },
    "meth": {
        "name": "🧪 Meth Lab",
        "price": 50000,
        "income": 3500, # $/h
        "desc": "Chemistry at its finest."
    },
    "cash": {
        "name": "💵 Counterfeit Cash",
        "price": 200000,
        "income": 15000, # $/h
        "desc": "Printing money involves inflation."
    },
    "nightclub": {
        "name": "💃 Nightclub",
        "price": 1000000,
        "income": 80000, # $/h
        "desc": "Perfect for laundering huge sums."
    }
}

# --- DEFINICJE KOMEND ---

CRIME_DATA = {
    "name": "crime",
    "description": "Commit a crime for quick cash (High Risk)",
    "type": 1
}

BUSINESS_DATA = {
    "name": "businesses",
    "description": "Manage your criminal empire",
    "type": 1
}

BUY_BIZ_DATA = {
    "name": "buy_business",
    "description": "Buy a new property",
    "type": 1,
    "options": [{
        "name": "type",
        "description": "Which business?",
        "type": 3,
        "required": True,
        "choices": [{"name": f"{b['name']} (${b['price']:,})", "value": k} for k, b in BUSINESSES.items()]
    }]
}

LAUNDER_DATA = {
    "name": "launder",
    "description": "Collect money from your businesses",
    "type": 1
}

# --- LOGIKA ---

def cmd_crime(data):
    user_id = data["member"]["user"]["id"]
    
    # Cooldown 10 minut
    can_crime, time_left = check_cooldown(user_id, "crime", 600)
    if not can_crime:
        mins = int(time_left // 60)
        secs = int(time_left % 60)
        return {"type": 4, "data": {"content": f"🚓 **Heat is too high!** Wait **{mins}m {secs}s** before next crime."}}

    # Szanse: 60% sukces, 40% porażka
    if random.random() < 0.6:
        earnings = random.randint(300, 1500)
        scenarios = [
            f"You robbed a gas station and got **${earnings}**.",
            f"You stole a car and sold parts for **${earnings}**.",
            f"You hacked an ATM and dispensed **${earnings}**."
        ]
        update_balance(user_id, earnings)
        msg = f"🔫 **SUCCESS!** {random.choice(scenarios)}"
        color = 0x2ecc71
    else:
        fine = random.randint(100, 500)
        update_balance(user_id, -fine)
        msg = f"🚓 **BUSTED!** The police caught you. You paid a **${fine}** bribe."
        color = 0xe74c3c

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "description": msg,
                "color": color
            }]
        }
    }

def cmd_businesses(data):
    user_id = data["member"]["user"]["id"]
    owned = get_businesses(user_id)
    
    if not owned:
        return {"type": 4, "data": {"content": "📉 You don't own any businesses. Use `/buy_business` to start your empire."}}

    desc = ""
    total_income = 0
    
    for biz_id, qty in owned.items():
        if biz_id in BUSINESSES:
            info = BUSINESSES[biz_id]
            income = info['income'] * qty
            total_income += income
            desc += f"**{info['name']}** x{qty}\nIncome: ${income:,}/h\n\n"
            
    desc += f"__**Total Passive Income:**__ ${total_income:,}/h\n"
    desc += "*Use `/launder` to collect your earnings.*"

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "🏭 Criminal Empire",
                "description": desc,
                "color": 0x9b59b6
            }]
        }
    }

def cmd_buy_business(data):
    user_id = data["member"]["user"]["id"]
    biz_type = data["options"][0]["value"]
    
    biz_info = BUSINESSES.get(biz_type)
    if not biz_info: return {"type": 4, "data": {"content": "Error"}}
    
    success, msg = buy_business_db(user_id, biz_type, biz_info['price'])
    
    if success:
        return {"type": 4, "data": {"content": f"✅ **Purchased!** You now own a **{biz_info['name']}**."}}
    else:
        return {"type": 4, "data": {"content": f"❌ **Failed:** {msg}"}}

def cmd_launder(data):
    user_id = data["member"]["user"]["id"]
    
    # Przygotuj mapę stawek {id: income}
    rates = {k: v['income'] for k, v in BUSINESSES.items()}
    
    earned, hourly = launder_money_db(user_id, rates)
    
    if earned > 0:
        return {
            "type": 4,
            "data": {
                "content": f"💵 **Money Laundered!**\nYou collected **${earned:,}** from your businesses.\n*(Generation Rate: ${hourly:,}/h)*"
            }
        }
    else:
        return {
            "type": 4,
            "data": {
                "content": "⏳ **No money to launder yet.**\nYour businesses generate money over time. Check back later!"
            }
        }