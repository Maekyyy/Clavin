import os
import time
import random
from google.cloud import firestore

# Inicjalizacja klienta Firestore
# Google Cloud automatycznie wykrywa dane logowania ze środowiska
db = firestore.Client()

# ==========================================
#              SYSTEM EKONOMII
# ==========================================

def get_balance(user_id):
    """Pobiera stan konta (gotówka)."""
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    return doc.to_dict().get('balance', 0) if doc.exists else 0

def get_bank_balance(user_id):
    """Pobiera stan konta w banku."""
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    return doc.to_dict().get('bank', 0) if doc.exists else 0

def update_balance(user_id, amount):
    """Aktualizuje gotówkę (dodaje/odejmuje)."""
    user_ref = db.collection('users').document(str(user_id))
    user_ref.set({'balance': firestore.Increment(amount)}, merge=True)

def bank_transaction(user_id, amount, direction):
    """Wpłata (deposit) lub wypłata (withdraw) z banku."""
    user_ref = db.collection('users').document(str(user_id))
    
    @firestore.transactional
    def tx_bank(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists: return False, "Brak konta"
        
        data = snapshot.to_dict()
        cash = data.get('balance', 0)
        bank = data.get('bank', 0)
        
        if direction == "deposit":
            if amount == "all": amount = cash
            amount = int(amount)
            if cash < amount: return False, "Za mało gotówki."
            if amount <= 0: return False, "Kwota musi być dodatnia."
            
            transaction.update(ref, {'balance': cash - amount, 'bank': bank + amount})
            return True, f"Wpłacono ${amount} do banku."
            
        elif direction == "withdraw":
            if amount == "all": amount = bank
            amount = int(amount)
            if bank < amount: return False, "Za mało środków w banku."
            if amount <= 0: return False, "Kwota musi być dodatnia."
            
            transaction.update(ref, {'balance': cash + amount, 'bank': bank - amount})
            return True, f"Wypłacono ${amount} z banku."

    transaction = db.transaction()
    return tx_bank(transaction, user_ref)

def claim_daily(user_id):
    """Odbiera nagrodę + 2% odsetek od kwoty w banku."""
    user_ref = db.collection('users').document(str(user_id))
    
    @firestore.transactional
    def tx_daily(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        data = snapshot.to_dict() if snapshot.exists else {}
        
        current_cash = data.get('balance', 0)
        current_bank = data.get('bank', 0)
        
        # Oblicz odsetki (max 5000)
        interest = int(current_bank * 0.02)
        if interest > 5000: interest = 5000
        
        # Dodaj 1000 (daily) + odsetki do banku
        transaction.set(ref, {
            'balance': current_cash + 1000,
            'bank': current_bank + interest
        }, merge=True)
        
        return current_bank + interest, interest

    transaction = db.transaction()
    return tx_daily(transaction, user_ref)

def transfer_money(sender_id, receiver_id, amount):
    """Atomowy przelew pieniędzy między użytkownikami."""
    sender_ref = db.collection('users').document(str(sender_id))
    receiver_ref = db.collection('users').document(str(receiver_id))

    @firestore.transactional
    def tx_transfer(transaction, send_ref, recv_ref):
        sender_snap = send_ref.get(transaction=transaction)
        if not sender_snap.exists: return False, "Konto nadawcy nie istnieje."
        
        sender_bal = sender_snap.to_dict().get('balance', 0)
        if sender_bal < amount: return False, "Brak środków."

        recv_snap = recv_ref.get(transaction=transaction)
        recv_bal = recv_snap.to_dict().get('balance', 0) if recv_snap.exists else 0

        transaction.set(send_ref, {'balance': sender_bal - amount}, merge=True)
        transaction.set(recv_ref, {'balance': recv_bal + amount}, merge=True)
        return True, "Sukces"

    transaction = db.transaction()
    return tx_transfer(transaction, sender_ref, receiver_ref)

def get_leaderboard(limit=10):
    """Zwraca listę najbogatszych użytkowników."""
    users_ref = db.collection('users')
    return users_ref.order_by('balance', direction=firestore.Query.DESCENDING).limit(limit).stream()

# ==========================================
#           COOLDOWNY I NARZĘDZIA
# ==========================================

def check_cooldown(user_id, command_name, cooldown_seconds):
    """Sprawdza czy komenda jest na cooldownie."""
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    now = int(time.time())
    
    if doc.exists:
        data = doc.to_dict()
        last_used = data.get(f'cd_{command_name}', 0)
        if now - last_used < cooldown_seconds:
            return False, cooldown_seconds - (now - last_used)
    
    user_ref.set({f'cd_{command_name}': now}, merge=True)
    return True, 0

# ==========================================
#        EKWIPUNEK I TYTUŁY (RPG)
# ==========================================

def get_inventory(user_id):
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    return doc.to_dict().get('inventory', []) if doc.exists else []

def add_item(user_id, item_id):
    user_ref = db.collection('users').document(str(user_id))
    user_ref.update({"inventory": firestore.ArrayUnion([item_id])})

def remove_item(user_id, item_id):
    user_ref = db.collection('users').document(str(user_id))
    user_ref.update({"inventory": firestore.ArrayRemove([item_id])})

def set_title(user_id, title):
    db.collection('users').document(str(user_id)).set({'title': title}, merge=True)

def get_title(user_id):
    doc = db.collection('users').document(str(user_id)).get()
    return doc.to_dict().get('title', "") if doc.exists else ""

# ==========================================
#           STAN GIER (Poker, itp.)
# ==========================================

def set_game_state(user_id, game_data):
    """Zapisuje stan gry z timestampem."""
    game_data['created_at'] = int(time.time())
    db.collection('games').document(str(user_id)).set(game_data)

def get_game_state(user_id):
    """Pobiera grę, usuwa stare (powyżej 10 min)."""
    doc_ref = db.collection('games').document(str(user_id))
    doc = doc_ref.get()
    
    if not doc.exists: return None
        
    data = doc.to_dict()
    created_at = data.get('created_at', 0)
    now = int(time.time())
    
    if now - created_at > 600: # 10 min TTL
        doc_ref.delete()
        return None
        
    return data

def delete_game_state(user_id):
    db.collection('games').document(str(user_id)).delete()

# ==========================================
#           RYNEK KRYPTOWALUT
# ==========================================

def get_crypto_price():
    """Pobiera aktualną cenę CC."""
    market_ref = db.collection('system').document('market')
    doc = market_ref.get()
    now = int(time.time())
    
    data = doc.to_dict() if doc.exists else {}
    price = data.get('price', 100)
    last_update = data.get('last_update', 0)
    
    if now - last_update > 600:
        change_percent = random.uniform(-0.1, 0.15)
        price = max(1, int(price * (1 + change_percent)))
        market_ref.set({'price': price, 'last_update': now})
        
    return price

def get_crypto_balance(user_id):
    doc = db.collection('users').document(str(user_id)).get()
    return doc.to_dict().get('crypto', 0) if doc.exists else 0

def update_crypto(user_id, amount):
    user_ref = db.collection('users').document(str(user_id))
    user_ref.update({"crypto": firestore.Increment(amount)})

# ==========================================
#           SYSTEM POZIOMÓW (XP)
# ==========================================

def add_xp(user_id, amount=10):
    """Dodaje XP i sprawdza awans."""
    user_ref = db.collection('users').document(str(user_id))
    
    @firestore.transactional
    def tx_xp(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        current_xp = 0
        current_lvl = 1
        
        if snapshot.exists:
            data = snapshot.to_dict()
            current_xp = data.get('xp', 0)
            current_lvl = data.get('level', 1)
        
        new_xp = current_xp + amount
        xp_needed = current_lvl * 100
        
        leveled_up = False
        if new_xp >= xp_needed:
            current_lvl += 1
            new_xp -= xp_needed
            leveled_up = True
            
        transaction.set(ref, {'xp': new_xp, 'level': current_lvl}, merge=True)
        return current_lvl, leveled_up

    transaction = db.transaction()
    return tx_xp(transaction, user_ref)

def get_level_data(user_id):
    doc = db.collection('users').document(str(user_id)).get()
    if doc.exists:
        data = doc.to_dict()
        return data.get('level', 1), data.get('xp', 0)
    return 1, 0

def get_xp_leaderboard(limit=10):
    return db.collection('users').order_by('level', direction=firestore.Query.DESCENDING).limit(limit).stream()

# ==========================================
#              SYSTEM ANKIET
# ==========================================

def create_poll(poll_id, question, options):
    db.collection('polls').document(poll_id).set({
        'question': question, 'options': options, 'votes': {}, 'created_at': int(time.time())
    })

def get_poll(poll_id):
    doc = db.collection('polls').document(poll_id).get()
    return doc.to_dict() if doc.exists else None

def add_vote(poll_id, user_id, option_index):
    poll_ref = db.collection('polls').document(poll_id)
    @firestore.transactional
    def tx_vote(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists: return False
        data = snapshot.to_dict()
        votes = data.get('votes', {})
        votes[str(user_id)] = option_index
        transaction.update(ref, {'votes': votes})
        return True
    transaction = db.transaction()
    return tx_vote(transaction, poll_ref)

# ==========================================
#           SYSTEM GTA (Biznesy)
# ==========================================

def get_businesses(user_id):
    doc = db.collection('users').document(str(user_id)).get()
    return doc.to_dict().get('businesses', {}) if doc.exists else {}

def buy_business_db(user_id, business_id, cost):
    user_ref = db.collection('users').document(str(user_id))
    @firestore.transactional
    def tx_buy_biz(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists: return False, "Brak konta"
        data = snapshot.to_dict()
        balance = data.get('balance', 0)
        businesses = data.get('businesses', {})
        if balance < cost: return False, "Niewystarczające środki"
        
        if not businesses: transaction.set(ref, {'last_launder': int(time.time())}, merge=True)
        businesses[business_id] = businesses.get(business_id, 0) + 1
        transaction.update(ref, {'balance': balance - cost, 'businesses': businesses})
        return True, "Sukces"
    transaction = db.transaction()
    return tx_buy_biz(transaction, user_ref)

def launder_money_db(user_id, rates):
    user_ref = db.collection('users').document(str(user_id))
    @firestore.transactional
    def tx_launder(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists: return 0, 0
        data = snapshot.to_dict()
        businesses = data.get('businesses', {})
        last_launder = data.get('last_launder', int(time.time()))
        current_balance = data.get('balance', 0)
        if not businesses: return 0, 0
        
        now = int(time.time())
        seconds = min(now - last_launder, 86400)
        total_income = sum(rates[bid] * qty for bid, qty in businesses.items() if bid in rates)
        earned = int((total_income / 3600) * seconds)
        
        if earned > 0: transaction.update(ref, {'balance': current_balance + earned, 'last_launder': now})
        return earned, total_income
    transaction = db.transaction()
    return tx_launder(transaction, user_ref)

# ==========================================
#           SPOŁECZNOŚĆ (Małżeństwa)
# ==========================================

def set_marriage(user1_id, user2_id):
    now = int(time.time())
    db.collection('users').document(str(user1_id)).update({'partner_id': str(user2_id), 'marriage_date': now})
    db.collection('users').document(str(user2_id)).set({'partner_id': str(user1_id), 'marriage_date': now}, merge=True)

def get_partner(user_id):
    doc = db.collection('users').document(str(user_id)).get()
    return doc.to_dict().get('partner_id') if doc.exists else None

def divorce_users(user1_id, user2_id):
    db.collection('users').document(str(user1_id)).update({'partner_id': firestore.DELETE_FIELD})
    db.collection('users').document(str(user2_id)).update({'partner_id': firestore.DELETE_FIELD})

def get_full_profile(user_id):
    doc = db.collection('users').document(str(user_id)).get()
    return doc.to_dict() if doc.exists else {}

# ==========================================
#           OSIĄGNIĘCIA I PREZENTY
# ==========================================

def transfer_item(sender_id, receiver_id, item_id):
    """Bezpiecznie przenosi przedmiot od nadawcy do odbiorcy."""
    sender_ref = db.collection('users').document(str(sender_id))
    receiver_ref = db.collection('users').document(str(receiver_id))
    
    @firestore.transactional
    def tx_transfer_item(transaction, send_ref, recv_ref):
        # 1. Pobierz dane nadawcy
        sender_snap = send_ref.get(transaction=transaction)
        if not sender_snap.exists: return False, "Sender has no account."
        
        sender_inv = sender_snap.to_dict().get('inventory', [])
        
        # 2. Sprawdź czy ma przedmiot
        if item_id not in sender_inv:
            return False, "You don't have this item."
            
        # 3. Pobierz dane odbiorcy (czy istnieje)
        recv_snap = recv_ref.get(transaction=transaction)
        if not recv_snap.exists:
            # Tworzymy puste konto dla odbiorcy
            transaction.set(recv_ref, {'inventory': []}, merge=True)
            
        # 4. Wykonaj transfer (Array Remove / Array Union nie działają idealnie wewnątrz transaction.update na listach lokalnych,
        # więc robimy to na pobranych danych).
        sender_inv.remove(item_id) # Usuń jedną sztukę
        
        transaction.update(send_ref, {'inventory': sender_inv})
        transaction.update(recv_ref, {'inventory': firestore.ArrayUnion([item_id])})
        
        return True, "Success"

    transaction = db.transaction()
    return tx_transfer_item(transaction, sender_ref, receiver_ref)

def get_achievements(user_id):
    """Pobiera listę odblokowanych osiągnięć (lista ID)."""
    doc = db.collection('users').document(str(user_id)).get()
    return doc.to_dict().get('achievements', []) if doc.exists else []

def unlock_achievement(user_id, achievement_id):
    """Dodaje osiągnięcie do profilu."""
    user_ref = db.collection('users').document(str(user_id))
    user_ref.update({"achievements": firestore.ArrayUnion([achievement_id])})
    
# ==========================================
#              SYSTEM LOTERII
# ==========================================

def get_lottery_state():
    """Pobiera stan loterii (pula, uczestnicy)."""
    doc = db.collection('system').document('lottery').get()
    if doc.exists:
        return doc.to_dict()
    return {"pot": 0, "tickets": []}

def buy_lottery_ticket(user_id, price=100):
    """Kupuje bilet. Jeśli to 10-ty bilet -> losuje zwycięzcę!"""
    user_ref = db.collection('users').document(str(user_id))
    lottery_ref = db.collection('system').document('lottery')
    
    @firestore.transactional
    def tx_buy_ticket(transaction, u_ref, l_ref):
        # 1. Sprawdź kasę usera
        u_snap = u_ref.get(transaction=transaction)
        if not u_snap.exists: return False, "No account"
        
        balance = u_snap.to_dict().get('balance', 0)
        if balance < price: return False, "Not enough cash"
        
        # 2. Pobierz stan loterii
        l_snap = l_ref.get(transaction=transaction)
        if l_snap.exists:
            l_data = l_snap.to_dict()
            pot = l_data.get('pot', 0)
            tickets = l_data.get('tickets', [])
        else:
            pot = 0
            tickets = []
            
        # 3. Aktualizuj (Kupno)
        new_balance = balance - price
        new_pot = pot + price
        tickets.append(str(user_id))
        
        transaction.update(u_ref, {'balance': new_balance})
        
        # 4. SPRAWDŹ CZY KONIEC (np. 10 biletów)
        if len(tickets) >= 10:
            winner_id = random.choice(tickets)
            
            # Wypłać zwycięzcy (musimy pobrać jego ref, jeśli to inna osoba niż kupujący)
            if winner_id == str(user_id):
                # Wygrał ten co kupił teraz
                transaction.update(u_ref, {'balance': new_balance + new_pot})
            else:
                # Wygrał ktoś inny (wymaga osobnego update, ale w transakcji to trudne dla dynamicznego ID)
                # UPROSZCZENIE: W Serverless transakcje na wielu losowych dokumentach są trudne.
                # Zrobimy to poza transakcją lub w uproszczony sposób:
                # Zapiszemy "pending_win" w dokumencie loterii i obsłużymy to osobno
                pass 
            
            # Reset loterii
            transaction.set(l_ref, {'pot': 0, 'tickets': []})
            return True, f"WINNER|{winner_id}|{new_pot}"
        else:
            # Po prostu dodaj bilet
            transaction.set(l_ref, {'pot': new_pot, 'tickets': tickets}, merge=True)
            return True, "TICKET"

    transaction = db.transaction()
    return tx_buy_ticket(transaction, user_ref, lottery_ref)

def payout_winner(winner_id, amount):
    """Wypłaca nagrodę zwycięzcy loterii (funkcja pomocnicza)."""
    user_ref = db.collection('users').document(str(winner_id))
    user_ref.update({'balance': firestore.Increment(amount)})