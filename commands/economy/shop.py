from database import get_balance, update_balance, add_item, get_inventory, set_title, get_title

# --- KATALOG PRODUKTÓW ---
# Tu definiujemy wszystko, co można kupić
SHOP_ITEMS = {
    # PRZEDMIOTY (Items)
    "shield": {
        "type": "item",
        "name": "🛡️ Shield",
        "price": 500,
        "desc": "Protects from one robbery"
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
    
    # Pobieramy dane użytkownika
    balance = get_balance(user_id)
    inventory = get_inventory(user_id)
    current_title = get_title(user_id)
    
    # Budujemy opis sklepu (Lista produktów)
    desc_items = ""
    desc_titles = ""
    
    # Przygotowujemy opcje do Select Menu
    select_options = []
    
    for key, item in SHOP_ITEMS.items():
        price = item['price']
        name = item['name']
        
        # Sprawdzamy czy użytkownik już to ma
        is_owned = False
        if item['type'] == "item" and key in inventory:
            is_owned = True
        elif item['type'] == "title" and current_title == item['value']:
            is_owned = True
            
        status = "✅ **OWNED**" if is_owned else f"💰 **${price:,}**"
        
        # Formatowanie tekstu do Embeda
        line = f"{name} — {status}\n*{item['desc']}*\n\n"
        
        if item['type'] == "item":
            desc_items += line
        else:
            desc_titles += line
            
        # Dodajemy do dropdowna tylko jeśli nie posiada (lub można mieć wiele - tu zakładamy unikalność)
        # Dla tytułów: pokazujemy wszystkie, ale oznaczymy w opisie
        if not is_owned:
            select_options.append({
                "label": f"{name.replace('Title: ', '')} (${price:,})",
                "value": key,
                "description": item['desc'][:50],
                "emoji": {"name": "🛒"}
            })

    # Jeśli użytkownik ma wszystko, dajemy pustą opcję
    if not select_options:
        select_options.append({
            "label": "You own everything!",
            "value": "empty",
            "description": "Rich people problems...",
            "emoji": {"name": "😎"}
        })

    # Budujemy Embed
    embed = {
        "title": "🛒 Clavin Global Market",
        "description": f"Your Balance: **${balance:,}**\n\n__**📦 ITEMS**__\n{desc_items}__**👑 TITLES**__\n{desc_titles}",
        "color": 0xf1c40f, # Gold
        "footer": {"text": "Select an item below to buy"}
    }
    
    # Komponent (Select Menu)
    components = [{
        "type": 1,
        "components": [{
            "type": 3, # String Select
            "custom_id": "shop_buy_select",
            "options": select_options,
            "placeholder": "Choose an item to buy..."
        }]
    }]

    return {
        "type": 4,
        "data": {
            "embeds": [embed],
            "components": components
        }
    }

# --- OBSŁUGA KUPNA (DROPDOWN) ---
def handle_shop_component(data):
    user_id = data["member"]["user"]["id"]
    selected_value = data["data"]["values"][0] # To co wybrał użytkownik (klucz np. 'shield')
    
    if selected_value == "empty":
        return {"type": 4, "data": {"content": "😎 You already have everything!", "flags": 64}}
        
    item = SHOP_ITEMS.get(selected_value)
    if not item:
        return {"type": 4, "data": {"content": "❌ Item not found.", "flags": 64}}
        
    price = item['price']
    balance = get_balance(user_id)
    
    # 1. Sprawdź kasę
    if balance < price:
        return {"type": 4, "data": {"content": f"❌ You need **${price:,}** but have **${balance:,}**.", "flags": 64}}
        
    # 2. Kupno w zależności od typu
    update_balance(user_id, -price)
    
    if item['type'] == "item":
        add_item(user_id, selected_value)
        msg = f"✅ **Successfully bought {item['name']}!**\nIt has been added to your inventory."
        
    elif item['type'] == "title":
        set_title(user_id, item['value'])
        msg = f"✅ **Successfully bought {item['name']}!**\nYour prefix has been updated."
        
    # 3. Odśwież sklep (zwracamy nową wersję wiadomości)
    # Wywołujemy cmd_shop jeszcze raz, żeby wygenerować zaktualizowany widok
    # Musimy tylko zasymulować strukturę 'data'
    fake_data = {"member": {"user": {"id": user_id}}}
    new_shop_view = cmd_shop(fake_data)
    
    # Podmieniamy typ odpowiedzi na Update Message (7)
    new_shop_view["type"] = 7
    
    # Opcjonalnie: Możemy wysłać ukrytą wiadomość o sukcesie lub zaktualizować sklep
    # Tu aktualizujemy sklep, żeby od razu pokazał "Owned"
    return new_shop_view