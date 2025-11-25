from database import get_balance, update_balance, add_item, get_inventory, set_title, get_title

# --- KATALOG PRODUKTÓW ---
SHOP_ITEMS = {
    # UŻYTKOWE (Items)
    "shield": {
        "type": "item",
        "name": "🛡️ Shield",
        "price": 500,
        "desc": "Protects from one robbery (One-use)"
    },
    "lockpick": {
        "type": "item",
        "name": "🧷 Lockpick",
        "price": 2500,
        "desc": "+15% chance to rob someone (Permanent)"
    },
    "fake_id": {
        "type": "item",
        "name": "🆔 Fake ID",
        "price": 5000,
        "desc": "-50% police fine when caught (Permanent)"
    },
    "vitamins": {
        "type": "item",
        "name": "💊 Vitamins",
        "price": 3000,
        "desc": "+50% salary in /work (Permanent)"
    },
    
    # TYTUŁY (Titles)
    "title_baron": {
        "type": "title",
        "name": "👑 Title: Baron",
        "value": "Baron",
        "price": 10000,
        "desc": "Prestige prefix"
    },
    "title_duke": {
        "type": "title",
        "name": "👑 Title: Duke",
        "value": "Duke",
        "price": 50000,
        "desc": "Prestige prefix"
    },
    "title_king": {
        "type": "title",
        "name": "👑 Title: King",
        "value": "King",
        "price": 100000,
        "desc": "Prestige prefix"
    },
    "title_god": {
        "type": "title",
        "name": "👑 Title: Godlike",
        "value": "Godlike",
        "price": 5000000,
        "desc": "Ultimate flex"
    }
}

SHOP_DATA = {
    "name": "shop",
    "description": "Open the Global Market (Items & Titles)",
    "type": 1
}

# --- GŁÓWNA KOMENDA ---
def cmd_shop(data):
    user_id = data["member"]["user"]["id"]
    balance = get_balance(user_id)
    inventory = get_inventory(user_id)
    current_title = get_title(user_id)
    
    desc_items = ""
    desc_titles = ""
    select_options = []
    
    for key, item in SHOP_ITEMS.items():
        price = item['price']
        name = item['name']
        
        is_owned = False
        if item['type'] == "item" and key in inventory:
            # Tarcze można kupować wielokrotnie (to wyjątek), reszta to stałe przedmioty
            if key != "shield": 
                is_owned = True
        elif item['type'] == "title" and current_title == item['value']:
            is_owned = True
            
        status = "✅ **OWNED**" if is_owned else f"💰 **${price:,}**"
        line = f"{name} — {status}\n*{item['desc']}*\n\n"
        
        if item['type'] == "item": desc_items += line
        else: desc_titles += line
            
        if not is_owned or key == "shield": # Pozwalamy kupić tarczę zawsze
            select_options.append({
                "label": f"{name.replace('Title: ', '')} (${price:,})",
                "value": key,
                "description": item['desc'][:50],
                "emoji": {"name": "🛒"}
            })

    if not select_options:
        select_options.append({"label": "Sold Out", "value": "empty", "emoji": {"name": "😎"}})

    embed = {
        "title": "🛒 Clavin Global Market",
        "description": f"Your Balance: **${balance:,}**\n\n__**📦 GEAR**__\n{desc_items}__**👑 TITLES**__\n{desc_titles}",
        "color": 0xf1c40f,
        "footer": {"text": "Select an item below to buy"}
    }
    
    components = [{"type": 1, "components": [{
        "type": 3, "custom_id": "shop_buy_select", "options": select_options[:25], "placeholder": "Choose an item..."
    }]}]

    return {"type": 4, "data": {"embeds": [embed], "components": components}}

# --- OBSŁUGA KUPNA ---
def handle_shop_component(data):
    user_id = data["member"]["user"]["id"]
    selected_value = data["data"]["values"][0]
    
    if selected_value == "empty": return {"type": 4, "data": {"content": "Nothing to buy.", "flags": 64}}
    item = SHOP_ITEMS.get(selected_value)
    if not item: return {"type": 4, "data": {"content": "❌ Error.", "flags": 64}}
        
    price = item['price']
    balance = get_balance(user_id)
    inventory = get_inventory(user_id)
    
    # Sprawdź czy już ma (dla unikalnych przedmiotów)
    if item['type'] == "item" and selected_value in inventory and selected_value != "shield":
        return {"type": 4, "data": {"content": f"❌ You already own **{item['name']}**!", "flags": 64}}

    if balance < price:
        return {"type": 4, "data": {"content": f"❌ You need **${price:,}**.", "flags": 64}}
        
    update_balance(user_id, -price)
    
    if item['type'] == "item":
        add_item(user_id, selected_value)
        msg = f"✅ **Bought {item['name']}!** Added to inventory."
    elif item['type'] == "title":
        set_title(user_id, item['value'])
        msg = f"✅ **New Title:** {item['name']} equipped!"
        
    fake_data = {"member": {"user": {"id": user_id}}}
    new_shop = cmd_shop(fake_data)
    new_shop["type"] = 7
    return new_shop