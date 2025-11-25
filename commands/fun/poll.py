import uuid
from database import create_poll, get_poll, add_vote

# --- DEFINICJA KOMENDY ---
POLL_DATA = {
    "name": "poll",
    "description": "Create a voting poll",
    "type": 1,
    "options": [
        {
            "name": "question",
            "description": "What do you want to ask?",
            "type": 3, # String
            "required": True
        },
        {
            "name": "option1", "description": "Choice 1", "type": 3, "required": True
        },
        {
            "name": "option2", "description": "Choice 2", "type": 3, "required": True
        },
        {
            "name": "option3", "description": "Choice 3", "type": 3, "required": False
        },
        {
            "name": "option4", "description": "Choice 4", "type": 3, "required": False
        }
    ]
}

# --- POMOCNICZE ---
def generate_poll_embed(poll_data):
    """Generuje wygląd ankiety z paskami postępu."""
    question = poll_data['question']
    options = poll_data['options']
    votes = poll_data.get('votes', {})
    
    total_votes = len(votes)
    
    # Liczenie głosów
    counts = [0] * len(options)
    for uid, opt_idx in votes.items():
        if 0 <= opt_idx < len(counts):
            counts[opt_idx] += 1
            
    # Budowanie opisu
    desc = ""
    for i, opt in enumerate(options):
        count = counts[i]
        percent = 0
        if total_votes > 0:
            percent = int((count / total_votes) * 100)
        
        bar = "🟦" * (percent // 10) + "⬜" * (10 - (percent // 10))
        desc += f"**{opt}**\n{bar} {percent}% ({count})\n\n"
        
    return {
        "title": f"📊 {question}",
        "description": desc,
        "color": 0x3498db,
        "footer": {"text": f"Total Votes: {total_votes}"}
    }

def generate_poll_buttons(poll_id, options):
    """Tworzy przyciski do głosowania."""
    buttons = []
    for i, opt in enumerate(options):
        buttons.append({
            "type": 2,
            "style": 1, # Blurple
            "label": opt[:80], # Limit znaków
            "custom_id": f"poll_{poll_id}_{i}"
        })
    return [{"type": 1, "components": buttons}]

# --- LOGIKA KOMENDY ---
def cmd_poll(data):
    # Pobieramy opcje
    raw_options = data.get("options", [])
    
    question = ""
    choices = []
    
    for opt in raw_options:
        if opt["name"] == "question":
            question = opt["value"]
        elif opt["name"].startswith("option"):
            choices.append(opt["value"])
            
    # Generujemy unikalne ID ankiety (krótkie)
    poll_id = str(uuid.uuid4())[:8]
    
    # Zapisz do bazy
    create_poll(poll_id, question, choices)
    
    # Przygotuj dane do wyświetlenia
    poll_data = {
        'question': question,
        'options': choices,
        'votes': {}
    }
    
    return {
        "type": 4,
        "data": {
            "embeds": [generate_poll_embed(poll_data)],
            "components": generate_poll_buttons(poll_id, choices)
        }
    }

# --- OBSŁUGA PRZYCISKÓW ---
def handle_poll_component(data):
    user_id = data["member"]["user"]["id"]
    custom_id = data["data"]["custom_id"]
    
    # custom_id format: poll_{ID}_{OPTION_INDEX}
    parts = custom_id.split("_")
    if len(parts) < 3: return {"type": 4, "data": {"content": "❌ Error"}}
    
    poll_id = parts[1]
    option_index = int(parts[2])
    
    # Zapisz głos
    success = add_vote(poll_id, user_id, option_index)
    
    if not success:
        return {"type": 4, "data": {"content": "❌ Poll expired or not found.", "flags": 64}}
        
    # Pobierz zaktualizowane dane i odśwież wiadomość
    poll_data = get_poll(poll_id)
    
    return {
        "type": 7, # Update Message
        "data": {
            "embeds": [generate_poll_embed(poll_data)],
            "components": generate_poll_buttons(poll_id, poll_data['options'])
        }
    }