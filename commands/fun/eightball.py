import random

EIGHTBALL_DATA = {
    "name": "8ball",
    "description": "Ask the magic 8-ball a question",
    "type": 1,
    "options": [{
        "name": "question",
        "description": "Your question",
        "type": 3, # String
        "required": True
    }]
}

ANSWERS = [
    "It is certain.", "It is decidedly so.", "Without a doubt.",
    "Yes definitely.", "You may rely on it.", "As I see it, yes.",
    "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
    "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
    "Cannot predict now.", "Concentrate and ask again.",
    "Don't count on it.", "My reply is no.", "My sources say no.",
    "Outlook not so good.", "Very doubtful."
]

def cmd_eightball(data):
    options = data.get("options", [])
    question = options[0]["value"]
    answer = random.choice(ANSWERS)
    
    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "🎱 Magic 8-Ball",
                "color": 0x000000,
                "fields": [
                    {"name": "Question", "value": question},
                    {"name": "Answer", "value": f"**{answer}**"}
                ]
            }]
        }
    }