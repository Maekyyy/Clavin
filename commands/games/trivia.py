import requests
import html
import random
from database import update_balance, set_game_state, get_game_state, delete_game_state, add_xp

TRIVIA_DATA = {
    "name": "trivia",
    "description": "Answer a question to win prizes!",
    "type": 1
}

def cmd_trivia(data):
    user_id = data["member"]["user"]["id"]
    
    # Sprawdź czy już gra
    if get_game_state(user_id):
        return {"type": 4, "data": {"content": "❌ Finish your current game first!"}}

    # Pobierz pytanie z Open Trivia DB
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    r = requests.get(url)
    if r.status_code != 200:
        return {"type": 4, "data": {"content": "❌ API Error."}}
        
    data = r.json()
    if not data["results"]:
        return {"type": 4, "data": {"content": "❌ No questions found."}}
        
    question_data = data["results"][0]
    question_text = html.unescape(question_data["question"])
    correct_answer = html.unescape(question_data["correct_answer"])
    incorrect_answers = [html.unescape(a) for a in question_data["incorrect_answers"]]
    
    # Wymieszaj odpowiedzi
    all_options = incorrect_answers + [correct_answer]
    random.shuffle(all_options)
    
    # Znajdź indeks poprawnej (0-3)
    correct_index = all_options.index(correct_answer)
    
    # Zapisz stan
    set_game_state(user_id, {
        "type": "trivia",
        "correct_index": correct_index,
        "difficulty": question_data["difficulty"]
    })
    
    # Przyciski
    buttons = []
    labels = ["A", "B", "C", "D"]
    for i, opt in enumerate(all_options):
        buttons.append({
            "type": 2,
            "style": 1,
            "label": f"{labels[i]}. {opt}"[:80],
            "custom_id": f"trivia_{i}"
        })

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": f"🧠 Trivia ({question_data['category']})",
                "description": f"**{question_text}**\n\nSelect the correct answer:",
                "color": 0x9b59b6,
                "footer": {"text": f"Difficulty: {question_data['difficulty'].upper()}"}
            }],
            "components": [{"type": 1, "components": buttons}]
        }
    }

def handle_trivia_component(data):
    user_id = data["member"]["user"]["id"]
    custom_id = data["data"]["custom_id"]
    
    game = get_game_state(user_id)
    if not game or game.get("type") != "trivia":
        return {"type": 4, "data": {"content": "❌ Time expired.", "flags": 64}}
        
    selected_index = int(custom_id.split("_")[1])
    correct_index = game["correct_index"]
    difficulty = game["difficulty"]
    
    delete_game_state(user_id)
    
    if selected_index == correct_index:
        # Nagrody zależne od trudności
        reward = 50 if difficulty == "easy" else 100 if difficulty == "medium" else 200
        update_balance(user_id, reward)
        add_xp(user_id, 20) # Bonus XP
        
        return {
            "type": 7,
            "data": {
                "content": f"✅ **CORRECT!**\nYou won **${reward}** and **20 XP**!",
                "components": []
            }
        }
    else:
        return {
            "type": 7,
            "data": {
                "content": f"❌ **WRONG!** Better luck next time.",
                "components": []
            }
        }