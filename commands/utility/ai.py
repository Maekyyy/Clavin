import os
import requests
import google.generativeai as genai
from threading import Thread

AI_DATA = {
    "name": "ask",
    "description": "Ask Clavin AI (Powered by Gemini)",
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
            
            # PRÓBA 1: Używamy modelu 'gemini-1.5-flash' (najnowszy standard)
            model_name = 'gemini-1.5-flash'
            model = genai.GenerativeModel(model_name)
            
            response = model.generate_content(question)
            text = response.text
            
            if len(text) > 1900:
                text = text[:1900] + "... (cut)"
                
            response_text = f"🧠 **Question:** {question}\n\n{text}"
            
        except Exception as e:
            # DIAGNOSTYKA: Jeśli model nie działa, sprawdzamy jakie są dostępne
            try:
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
                
                models_str = ", ".join(available_models)
                response_text = f"❌ AI Error: {str(e)}\n\n**Available Models:** {models_str}"
            except:
                response_text = f"❌ AI Error (Critical): {str(e)}"

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