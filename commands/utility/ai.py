import os
import requests
import google.generativeai as genai
from threading import Thread

# --- DEFINICJA KOMENDY ---
AI_DATA = {
    "name": "ask",
    "description": "Ask Clavin AI (Powered by Gemini)",
    "type": 1,
    "options": [{
        "name": "question",
        "description": "What do you want to know?",
        "type": 3, # String
        "required": True
    }]
}

# --- FUNKCJA W TLE (To dzieje się po cichu) ---
def process_ai_response(interaction_token, app_id, question):
    """Wysyła zapytanie do AI i edytuje wiadomość na Discordzie."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        response_text = "❌ Error: Missing GOOGLE_API_KEY in configuration."
    else:
        try:
            # Konfiguracja Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash') # Szybki i darmowy model
            
            # Generowanie (limit znaków dla Discorda to 2000)
            response = model.generate_content(question)
            text = response.text
            
            if len(text) > 1900:
                text = text[:1900] + "... (message too long)"
                
            response_text = f"🧠 **Question:** {question}\n\n{text}"
            
        except Exception as e:
            response_text = f"❌ AI Error: {str(e)}"

    # WYSYŁAMY ODPOWIEDŹ DO DISCORDA (PATCH)
    # Używamy tokena interakcji, żeby edytować wiadomość "Thinking..."
    url = f"https://discord.com/api/v10/webhooks/{app_id}/{interaction_token}/messages/@original"
    requests.patch(url, json={"content": response_text})

# --- GŁÓWNA FUNKCJA ---
def cmd_ask(data):
    # Pobieramy dane potrzebne do odpowiedzi w tle
    token = data.get("token") # Token interakcji (ważny 15 min)
    app_id = data.get("application_id")
    
    # Pobieramy pytanie
    options = data.get("options", [])
    question = options[0]["value"]
    
    # Uruchamiamy AI w oddzielnym wątku, żeby nie blokować bota
    # (W Cloud Run CPU może zostać uśpione, ale dla krótkich zapytań zazwyczaj działa)
    thread = Thread(target=process_ai_response, args=(token, app_id, question))
    thread.start()

    # Zwracamy TYP 5 (DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE)
    # To wyświetli użytkownikowi "Clavin is thinking..."
    return {
        "type": 5
    }