import os
import requests
import google.generativeai as genai
from threading import Thread

AI_DATA = {
    "name": "ask",
    "description": "Ask Clavin AI (Powered by Gemini 3.0 Pro)",
    "type": 1,
    "options": [{
        "name": "question",
        "description": "What do you want to know?",
        "type": 3,
        "required": True
    }]
}

def process_ai_response(interaction_token, app_id, question):
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        response_text = "❌ Error: Missing GOOGLE_API_KEY."
    else:
        try:
            genai.configure(api_key=api_key)
            
            # USTAWIAMY MODEL GEMINI 3.0 PRO (z Twojej listy)
            model_name = 'gemini-3-pro-preview'
            model = genai.GenerativeModel(model_name)
            
            response = model.generate_content(question)
            text = response.text
            
            # Przycinanie (Discord ma limit 2000 znaków)
            if len(text) > 1900:
                text = text[:1900] + "... (message too long)"
                
            response_text = f"🧠 **Gemini 3.0:** {question}\n\n{text}"
            
        except Exception as e:
            # Diagnostyka w razie błędu
            response_text = f"❌ AI Error ({model_name}): {str(e)}"

    # Wysyłanie odpowiedzi
    url = f"https://discord.com/api/v10/webhooks/{app_id}/{interaction_token}/messages/@original"
    requests.patch(url, json={"content": response_text})

def cmd_ask(data):
    token = data.get("token")
    app_id = data.get("application_id")
    options = data.get("options", [])
    question = options[0]["value"]
    
    thread = Thread(target=process_ai_response, args=(token, app_id, question))
    thread.start()

    return {"type": 5}