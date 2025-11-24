import os
from google.cloud import firestore

db = firestore.Client()

def get_balance(user_id):
    """Sprawdza stan konta."""
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    return doc.to_dict().get('balance', 0) if doc.exists else 0

def update_balance(user_id, amount):
    """Dodaje/Odejmuje środki (Atomowo)."""
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

# --- NOWE FUNKCJE ---

def transfer_money(sender_id, receiver_id, amount):
    """Bezpieczny przelew między użytkownikami."""
    sender_ref = db.collection('users').document(str(sender_id))
    receiver_ref = db.collection('users').document(str(receiver_id))

    @firestore.transactional
    def tx_transfer(transaction, send_ref, recv_ref):
        # 1. Sprawdź nadawcę
        sender_snap = send_ref.get(transaction=transaction)
        if not sender_snap.exists:
            return False, "Nie masz konta (użyj /daily)."
        
        sender_bal = sender_snap.to_dict().get('balance', 0)
        if sender_bal < amount:
            return False, "Brak środków."

        # 2. Sprawdź odbiorcę (czy istnieje w bazie)
        # Jeśli nie istnieje, tworzymy mu konto z 0 + przelew
        recv_snap = recv_ref.get(transaction=transaction)
        recv_bal = recv_snap.to_dict().get('balance', 0) if recv_snap.exists else 0

        # 3. Wykonaj przelew
        transaction.set(send_ref, {'balance': sender_bal - amount}, merge=True)
        transaction.set(recv_ref, {'balance': recv_bal + amount}, merge=True)
        
        return True, "Sukces"

    transaction = db.transaction()
    return tx_transfer(transaction, sender_ref, receiver_ref)

def get_leaderboard(limit=10):
    """Pobiera top użytkowników."""
    users_ref = db.collection('users')
    # Sortuj malejąco po balance i weź top X
    query = users_ref.order_by('balance', direction=firestore.Query.DESCENDING).limit(limit)
    return query.stream()

# --- FUNKCJE GRY (POKER) ---
def set_game_state(user_id, game_data):
    db.collection('games').document(str(user_id)).set(game_data)

def get_game_state(user_id):
    doc = db.collection('games').document(str(user_id)).get()
    return doc.to_dict() if doc.exists else None

def delete_game_state(user_id):
    db.collection('games').document(str(user_id)).delete()