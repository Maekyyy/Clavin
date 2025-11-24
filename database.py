import os
from google.cloud import firestore

# Google Cloud automatycznie wykryje projekt i uprawnienia!
db = firestore.Client()

def get_balance(user_id):
    """Sprawdza stan konta użytkownika. Jeśli nie ma konta, tworzy je z 0."""
    user_ref = db.collection('users').document(str(user_id))
    doc = user_ref.get()
    
    if doc.exists:
        return doc.to_dict().get('balance', 0)
    else:
        # Nowy użytkownik zaczyna z 0 (musi wpisać /daily)
        return 0

def update_balance(user_id, amount):
    """Dodaje lub odejmuje pieniądze. Zwraca nowy stan konta."""
    user_ref = db.collection('users').document(str(user_id))
    
    # Używamy transakcji, żeby nie zgubić pieniędzy przy szybkim klikaniu
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
    """Sprawdza czy można odebrać nagrodę dzienną (uproszczone: zawsze daje 1000)"""
    # W wersji PRO tutaj sprawdzalibyśmy datę ostatniego odbioru.
    # Na razie dla prostoty: po prostu daje 1000.
    return update_balance(user_id, 1000)

# --- NOWE FUNKCJE DLA GRY ---

def set_game_state(user_id, game_data):
    """Zapisuje aktualny stan gry (karty, zakład) w bazie."""
    # Zapisujemy w nowej kolekcji 'games'
    db.collection('games').document(str(user_id)).set(game_data)

def get_game_state(user_id):
    """Pobiera trwającą grę."""
    doc = db.collection('games').document(str(user_id)).get()
    if doc.exists:
        return doc.to_dict()
    return None

def delete_game_state(user_id):
    """Czyści grę po zakończeniu (żeby nie zajmowała miejsca)."""
    db.collection('games').document(str(user_id)).delete()