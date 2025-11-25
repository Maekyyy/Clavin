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
    """Pobiera stan konta użytkownika."""
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    return doc.to_dict().get('balance', 0) if doc.exists else 0

def update_balance(user_id, amount):
    """Bezpiecznie dodaje lub odejmuje pieniądze używając transakcji."""
    user_ref = db.collection('users').document(str(user_id))
    
    @firestore.transactional
    def update_in_transaction(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        new_balance = amount
        if snapshot.exists:
            new_balance = snapshot.to_dict().get('balance', 0) + amount
        
        transaction.set(ref, {'balance': new_balance}, merge=True)
        return new_balance

    transaction = db.transaction()
    return update_in_transaction(transaction, user_ref)

def claim_daily(user_id):
    """Dodaje 1000 żetonów do konta użytkownika."""
    return update_balance(user_id, 1000)

def transfer_money(sender_id, receiver_id, amount):
    """Atomowy przelew pieniędzy między dwoma użytkownikami."""
    sender_ref = db.collection('users').document(str(sender_id))
    receiver_ref = db.collection('users').document(str(receiver_id))

    @firestore.transactional
    def tx_transfer(transaction, send_ref, recv_ref):
        # Sprawdź nadawcę
        sender_snap = send_ref.get(transaction=transaction)
        if not sender_snap.exists: return False, "Konto nie istnieje."
        
        sender_bal = sender_snap.to_dict().get('balance', 0)
        if sender_bal < amount: return False, "Niewystarczające środki."

        # Sprawdź odbiorcę (utwórz jeśli nie istnieje)
        recv_snap = recv_ref.get(transaction=transaction)
        recv_bal = recv_snap.to_dict().get('balance', 0) if recv_snap.exists else 0

        # Wykonaj przelew
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
    """Sprawdza czy komenda jest na cooldownie. Zwraca (dozwolone, czas_do_końca)."""
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
    db.collection('games').document(str(user_id)).set(game_data)

def get_game_state(user_id):
    doc = db.collection('games').document(str(user_id)).get()
    return doc.to_dict() if doc.exists else None

def delete_game_state(user_id):
    db.collection('games').document(str(user_id)).delete()

# ==========================================
#           RYNEK KRYPTOWALUT
# ==========================================

def get_crypto_price():
    """Pobiera aktualną cenę. Symuluje wahania jeśli dane są stare."""
    market_ref = db.collection('system').document('market')
    doc = market_ref.get()
    now = int(time.time())
    
    data = doc.to_dict() if doc.exists else {}
    price = data.get('price', 100)
    last_update = data.get('last_update', 0)
    
    # Aktualizuj cenę co 10 minut (600 sekund)
    if now - last_update > 600:
        change_percent = random.uniform(-0.1, 0.15) # -10% do +15%
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
    """Dodaje XP i sprawdza czy nastąpił awans. Zwraca (nowy_poziom, czy_awansował)."""
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
    """Tworzy nową ankietę w bazie."""
    db.collection('polls').document(poll_id).set({
        'question': question,
        'options': options, # Lista opcji
        'votes': {}, # Mapa user_id -> option_index
        'created_at': int(time.time())
    })

def get_poll(poll_id):
    """Pobiera dane ankiety."""
    doc = db.collection('polls').document(poll_id).get()
    return doc.to_dict() if doc.exists else None

def add_vote(poll_id, user_id, option_index):
    """Zapisuje głos użytkownika (nadpisuje poprzedni)."""
    poll_ref = db.collection('polls').document(poll_id)
    
    @firestore.transactional
    def tx_vote(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists: return False
        
        data = snapshot.to_dict()
        votes = data.get('votes', {})
        
        # Zapisz głos (str(user_id) jako klucz)
        votes[str(user_id)] = option_index
        
        transaction.update(ref, {'votes': votes})
        return True

    transaction = db.transaction()
    return tx_vote(transaction, poll_ref)

# ==========================================
#           SYSTEM GTA (Biznesy)
# ==========================================

def get_businesses(user_id):
    """Pobiera listę posiadanych biznesów."""
    doc = db.collection('users').document(str(user_id)).get()
    # Zwraca słownik: {'weed_farm': 1, 'meth_lab': 0}
    return doc.to_dict().get('businesses', {}) if doc.exists else {}

def buy_business_db(user_id, business_id, cost):
    """Kupuje biznes i aktualizuje stan konta."""
    user_ref = db.collection('users').document(str(user_id))
    
    @firestore.transactional
    def tx_buy_biz(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists: return False, "Brak konta"
        
        data = snapshot.to_dict()
        balance = data.get('balance', 0)
        businesses = data.get('businesses', {})
        
        if balance < cost:
            return False, "Niewystarczające środki"
            
        # Przygotuj aktualizacje
        updates = {}
        
        # Jeśli to pierwszy biznes, ustaw czas startu
        if not businesses:
            updates['last_launder'] = int(time.time())
            
        # Dodaj biznes
        current_qty = businesses.get(business_id, 0)
        businesses[business_id] = current_qty + 1
        
        updates['businesses'] = businesses
        updates['balance'] = balance - cost
        
        transaction.set(ref, updates, merge=True)
        return True, "Sukces"

    transaction = db.transaction()
    return tx_buy_biz(transaction, user_ref)

def launder_money_db(user_id, rates):
    """Oblicza i wypłaca zarobione pieniądze."""
    user_ref = db.collection('users').document(str(user_id))
    
    @firestore.transactional
    def tx_launder(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists: return 0, 0
        
        data = snapshot.to_dict()
        businesses = data.get('businesses', {})
        last_launder = data.get('last_launder', int(time.time()))
        current_balance = data.get('balance', 0)
        
        if not businesses:
            return 0, 0
            
        # Oblicz zarobek
        now = int(time.time())
        seconds_passed = now - last_launder
        
        # Limit czasu (np. max 24h akumulacji)
        if seconds_passed > 86400: seconds_passed = 86400
        
        # Sumuj dochód godzinowy
        total_hourly_income = 0
        for biz_id, qty in businesses.items():
            if biz_id in rates:
                total_hourly_income += rates[biz_id] * qty
                
        # Przelicz na sekundy
        earned = int((total_hourly_income / 3600) * seconds_passed)
        
        if earned > 0:
            transaction.update(ref, {
                'balance': current_balance + earned,
                'last_launder': now
            })
            
        return earned, total_hourly_income

    transaction = db.transaction()
    return tx_launder(transaction, user_ref)

# ==========================================
#           SPOŁECZNOŚĆ (Małżeństwa)
# ==========================================

def set_marriage(user1_id, user2_id):
    """Ustawia partnerów dla obu użytkowników."""
    now = int(time.time())
    # Zapisz u użytkownika 1
    db.collection('users').document(str(user1_id)).update({
        'partner_id': str(user2_id),
        'marriage_date': now
    })
    # Zapisz u użytkownika 2
    db.collection('users').document(str(user2_id)).set({
        'partner_id': str(user1_id),
        'marriage_date': now
    }, merge=True)

def get_partner(user_id):
    """Zwraca ID partnera lub None."""
    doc = db.collection('users').document(str(user_id)).get()
    return doc.to_dict().get('partner_id') if doc.exists else None

def divorce_users(user1_id, user2_id):
    """Usuwa małżeństwo."""
    db.collection('users').document(str(user1_id)).update({'partner_id': firestore.DELETE_FIELD})
    db.collection('users').document(str(user2_id)).update({'partner_id': firestore.DELETE_FIELD})

def get_full_profile(user_id):
    """Pobiera wszystkie dane użytkownika do komendy /profile."""
    doc = db.collection('users').document(str(user_id)).get()
    if not doc.exists:
        return {}
    return doc.to_dict()