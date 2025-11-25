import os
import time
import random
from google.cloud import firestore

# Initialize Firestore Client
# Google Cloud automatically detects credentials from the environment
db = firestore.Client()

# ==========================================
#              ECONOMY SYSTEM
# ==========================================

def get_balance(user_id):
    """Retrieves user's wallet balance."""
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    return doc.to_dict().get('balance', 0) if doc.exists else 0

def update_balance(user_id, amount):
    """Safely adds or removes money using transactions."""
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
    """Adds 1000 chips to user balance."""
    return update_balance(user_id, 1000)

def transfer_money(sender_id, receiver_id, amount):
    """Transfers money between two users atomically."""
    sender_ref = db.collection('users').document(str(sender_id))
    receiver_ref = db.collection('users').document(str(receiver_id))

    @firestore.transactional
    def tx_transfer(transaction, send_ref, recv_ref):
        # Check Sender
        sender_snap = send_ref.get(transaction=transaction)
        if not sender_snap.exists: return False, "Account not found."
        
        sender_bal = sender_snap.to_dict().get('balance', 0)
        if sender_bal < amount: return False, "Insufficient funds."

        # Check Receiver (create if not exists)
        recv_snap = recv_ref.get(transaction=transaction)
        recv_bal = recv_snap.to_dict().get('balance', 0) if recv_snap.exists else 0

        # Execute Transfer
        transaction.set(send_ref, {'balance': sender_bal - amount}, merge=True)
        transaction.set(recv_ref, {'balance': recv_bal + amount}, merge=True)
        return True, "Success"

    transaction = db.transaction()
    return tx_transfer(transaction, sender_ref, receiver_ref)

def get_leaderboard(limit=10):
    """Returns the top richest users."""
    users_ref = db.collection('users')
    return users_ref.order_by('balance', direction=firestore.Query.DESCENDING).limit(limit).stream()

# ==========================================
#           COOLDOWNS & UTILS
# ==========================================

def check_cooldown(user_id, command_name, cooldown_seconds):
    """Checks if a command is on cooldown. Returns (allowed, time_left)."""
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
#        INVENTORY & TITLES (RPG)
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
#           GAME STATE (Poker, etc.)
# ==========================================

def set_game_state(user_id, game_data):
    db.collection('games').document(str(user_id)).set(game_data)

def get_game_state(user_id):
    doc = db.collection('games').document(str(user_id)).get()
    return doc.to_dict() if doc.exists else None

def delete_game_state(user_id):
    db.collection('games').document(str(user_id)).delete()

# ==========================================
#           CRYPTO MARKET
# ==========================================

def get_crypto_price():
    """Gets current price. Simulates fluctuation if data is old."""
    market_ref = db.collection('system').document('market')
    doc = market_ref.get()
    now = int(time.time())
    
    data = doc.to_dict() if doc.exists else {}
    price = data.get('price', 100)
    last_update = data.get('last_update', 0)
    
    # Update price every 10 minutes (600 seconds)
    if now - last_update > 600:
        change_percent = random.uniform(-0.1, 0.15) # -10% to +15%
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
#           LEVELING SYSTEM (XP)
# ==========================================

def add_xp(user_id, amount=10):
    """Adds XP and checks for level up. Returns (new_level, leveled_up_bool)."""
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
#              POLL SYSTEM
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
#           GTA SYSTEM (Businesses)
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
        if not snapshot.exists: return False, "No account"
        
        data = snapshot.to_dict()
        balance = data.get('balance', 0)
        businesses = data.get('businesses', {})
        
        if balance < cost:
            return False, "Not enough cash"
            
        # Jeśli to pierwszy biznes, ustawiamy czas startu dochodu
        if not businesses:
            transaction.set(ref, {'last_launder': int(time.time())}, merge=True)
            
        # Dodajemy biznes (lub zwiększamy ilość, jeśli chcesz pozwalać na wiele)
        # Tutaj zakładamy 1 typ = 1 sztuka dla uproszczenia, lub zliczamy
        current_qty = businesses.get(business_id, 0)
        businesses[business_id] = current_qty + 1
        
        transaction.update(ref, {
            'balance': balance - cost,
            'businesses': businesses
        })
        return True, "Success"

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
            
        # Obliczamy zarobek
        now = int(time.time())
        seconds_passed = now - last_launder
        
        # Limit czasu (np. max 24h akumulacji, żeby zmuszać do logowania)
        if seconds_passed > 86400: seconds_passed = 86400
        
        # Sumujemy dochód na godzinę (rates to słownik id -> $/h)
        total_hourly_income = 0
        for biz_id, qty in businesses.items():
            if biz_id in rates:
                total_hourly_income += rates[biz_id] * qty
                
        # Przeliczamy na sekundy
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
#           SOCIAL (MARRIAGE)
# ==========================================

def set_marriage(user1_id, user2_id):
    """Ustawia partnerów dla obu użytkowników."""
    now = int(time.time())
    # Zapisz u użytkownika 1
    db.collection('users').document(str(user1_id)).update({
        'partner_id': str(user2_id),
        'marriage_date': now
    })
    # Zapisz u użytkownika 2 (jeśli dokument nie istnieje, set z merge=True go stworzy)
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