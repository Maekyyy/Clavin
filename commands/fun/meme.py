import requests

MEME_DATA = {
    "name": "meme",
    "description": "Generate a meme",
    "type": 1,
    "options": [
        {
            "name": "template",
            "description": "Meme template",
            "type": 3,
            "required": True,
            "choices": [
                {"name": "Doge", "value": "doge"},
                {"name": "Drake Hotline Bling", "value": "drake"},
                {"name": "Distracted Boyfriend", "value": "distracted"},
                {"name": "Two Buttons", "value": "two-buttons"},
                {"name": "Woman Yelling At Cat", "value": "woman-yelling"},
                {"name": "Change My Mind", "value": "change-my-mind"},
                {"name": "Batman Slapping Robin", "value": "batman"},
                {"name": "Mocking Spongebob", "value": "mocking-spongebob"}
            ]
        },
        {
            "name": "top_text",
            "description": "Text on top",
            "type": 3,
            "required": True
        },
        {
            "name": "bottom_text",
            "description": "Text on bottom",
            "type": 3,
            "required": False
        }
    ]
}

def cmd_meme(data):
    options = data.get("options", [])
    template = options[0]["value"]
    top = options[1]["value"]
    bottom = ""
    
    if len(options) > 2:
        bottom = options[2]["value"]

    # Formatowanie URL (zamiana spacji na _, specjalnych znaków itp.)
    def clean(text):
        return text.strip().replace("_", "__").replace("-", "--").replace(" ", "_").replace("?", "~q").replace("%", "~p").replace("#", "~h").replace("/", "~s")

    safe_top = clean(top)
    safe_bottom = clean(bottom) if bottom else "_"
    
    # API Memegen
    image_url = f"https://api.memegen.link/images/{template}/{safe_top}/{safe_bottom}.png"

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "🤣 Meme Generator",
                "image": {"url": image_url},
                "color": 0xf1c40f,
                "footer": {"text": f"Template: {template}"}
            }]
        }
    }