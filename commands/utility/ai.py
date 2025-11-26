import os
import requests
import google.generativeai as genai
from threading import Thread

AI_DATA = {
    "name": "ask",
    "description": "Ask Clavin AI (Powered by Gemini 3.0)",
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
    
    embed = {}
    
    if not api_key:
        content = "❌ Error: Missing GOOGLE_API_KEY."
        payload = {"content": content}
    else:
        try:
            genai.configure(api_key=api_key)
            
            # Model
            model_name = 'gemini-3-pro-preview'
            model = genai.GenerativeModel(model_name)
            
            response = model.generate_content(question)
            text = response.text
            
            # Limit Embeda to 4096 znaków. Ucinamy przy 4000 dla marginesu.
            if len(text) > 4000:
                text = text[:4000] + "\n\n... (text limit reached)"
            
            # Tworzymy ładny Embed zamiast zwykłego tekstu
            embed = {
                "title": f"🧠 {question[:250]}", # Tytuł to pytanie (max 256 znaków)
                "description": text,
                "color": 0x3498db, # Niebieski
                "footer": {"text": f"Model: {model_name}"}
            }
            
            payload = {"embeds": [embed]}
            
        except Exception as e:
            # Obsługa błędów (nadal jako zwykły tekst, żeby było widać co się stało)
            payload = {"content": f"❌ AI Error: {str(e)}"}

    # Wysyłanie odpowiedzi (PATCH)
    url = f"https://discord.com/api/v10/webhooks/{app_id}/{interaction_token}/messages/@original"
    requests.patch(url, json=payload)

def cmd_ask(data):
    token = data.get("token")
    app_id = data.get("application_id")
    options = data.get("options", [])
    question = options[0]["value"]
    
    thread = Thread(target=process_ai_response, args=(token, app_id, question))
    thread.start()

    return {"type": 5}