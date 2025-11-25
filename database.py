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