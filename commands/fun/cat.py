import requests

# --- DEFINICJA KOMENDY ---
CAT_DATA = {
    "name": "cat",
    "description": "Shows a random cat picture or gif",
    "type": 1
}

# --- LOGIKA ---
def cmd_cat(data):
    # Używamy publicznego API do kotków
    url = "https://api.thecatapi.com/v1/images/search"
    
    try:
        # Pobieramy dane
        r = requests.get(url)
        
        if r.status_code == 200:
            # API zwraca listę z jednym obiektem: [{"url": "..."}]
            data = r.json()
            image_url = data[0]['url']
            
            return {
                "type": 4,
                "data": {
                    "embeds": [
                        {
                            "title": "🐱 Meow!",
                            "color": 0xf1c40f,  # Złoty kolor
                            "image": {
                                "url": image_url
                            },
                            "footer": {
                                "text": "Powered by The Cat API"
                            }
                        }
                    ]
                }
            }
        else:
            return {
                "type": 4,
                "data": {"content": "😿 The cats are sleeping (API Error). Try again later."}
            }
            
    except Exception:
        return {
            "type": 4,
            "data": {"content": "😿 Something went wrong while fetching the cat."}
        }