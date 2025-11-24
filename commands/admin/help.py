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
                    "color": 0x3498db,  # Blue
                    "fields": [
                        {
                            "name": "💰 Economy Module",
                            "value": "`/balance` `/daily` `/pay` `/richlist`\n`/work` - Earn money\n`/shop` - Buy items\n`/rob` - Steal from others!",
                            "inline": False
                        },
                        {
                            "name": "🎉 Fun Module",
                            "value": "`/poker` `/roulette` `/coinflip` `/cat` `/hello`",
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