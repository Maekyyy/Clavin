HELP_DATA = {
    "name": "help",
    "description": "Displays the list of available commands",
    "type": 1
}

def cmd_help(data):
    return {
        "type": 4,
        "data": {
            "embeds": [
                {
                    "title": "📜 Clavin Bot Command List",
                    "description": "Here is a list of all available bot functions:",
                    "color": 0x3498db,  # Blue color
                    "fields": [
                        {
                            "name": "🎉 Fun Module",
                            "value": "`/hello` - Say hello to the bot\n`/poker` - Play a hand of cards", # <--- ZMIANA
                            "inline": False
                        },
                        {
                            "name": "⚙️ Root Module",
                            "value": "`/synctest` - Check connection status",
                            "inline": False
                        },
                        {
                            "name": "🛡️ Admin Module",
                            "value": "`/serverinfo` - Server information\n`/help` - Displays this list",
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": "Running on Google Cloud Run"
                    }
                }
            ]
        }
    }