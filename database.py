import os
import time
from google.cloud import firestore

db = firestore.Client()

# --- PODSTAWOWE FINANSE ---
def get_balance(user_id):
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    return doc.to_dict().get('balance', 0) if doc.exists else 0

def update_balance(user_id, amount):
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
    return update_balance(user_id, 1000)

def transfer_money(sender_id, receiver_id, amount):
    sender_ref = db.collection('users').document(str(sender_id))
    receiver_ref = db.collection('users').document(str(receiver_id))

    @firestore.transactional
    def tx_transfer(transaction, send_ref, recv_ref):
        sender_snap = send_ref.get(transaction=transaction)
        if not sender_snap.exists: return False, "No account."
        
        sender_bal = sender_snap.to_dict().get('balance', 0)
        if sender_bal < amount: return False, "Not enough money."

        recv_snap = recv_ref.get(transaction=transaction)
        recv_bal = recv_snap.to_dict().get('balance', 0) if recv_snap.exists else 0

        transaction.set(send_ref, {'balance': sender_bal - amount}, merge=True)
        transaction.set(recv_ref, {'balance': recv_bal + amount}, merge=True)
        return True, "Success"

    transaction = db.transaction()
    return tx_transfer(transaction, sender_ref, receiver_ref)

def get_leaderboard(limit=10):
    users_ref = db.collection('users')
    return users_ref.order_by('balance', direction=firestore.Query.DESCENDING).limit(limit).stream()

# --- NOWE: CZAS (COOLDOWNS) ---
def check_cooldown(user_id, command_name, cooldown_seconds):
    """Sprawdza czy można użyć komendy. Zwraca (True, 0) lub (False, czas_do_końca)."""
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    
    now = int(time.time())
    
    if doc.exists:
        data = doc.to_dict()
        last_used = data.get(f'cd_{command_name}', 0)
        if now - last_used < cooldown_seconds:
            return False, cooldown_seconds - (now - last_used)
    
    # Zapisz nowy czas użycia
    user_ref.set({f'cd_{command_name}': now}, merge=True)
    return True, 0

# --- NOWE: EKWIPUNEK (SHOP) ---
def get_inventory(user_id):
    """Zwraca listę przedmiotów użytkownika."""
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    if doc.exists:
        return doc.to_dict().get('inventory', [])
    return []

def add_item(user_id, item_id):
    """Dodaje przedmiot do ekwipunku."""
    user_ref = db.collection('users').document(str(user_id))
    # Firestore array_union dodaje element tylko jeśli go nie ma (unikalne)
    user_ref.update({"inventory": firestore.ArrayUnion([item_id])})

def remove_item(user_id, item_id):
    """Usuwa przedmiot (np. zużytą tarczę)."""
    user_ref = db.collection('users').document(str(user_id))
    user_ref.update({"inventory": firestore.ArrayRemove([item_id])})

# --- GRY (POKER) ---
def set_game_state(user_id, game_data):
    db.collection('games').document(str(user_id)).set(game_data)

def get_game_state(user_id):
    doc = db.collection('games').document(str(user_id)).get()
    return doc.to_dict() if doc.exists else None

def delete_game_state(user_id):
    db.collection('games').document(str(user_id)).delete()