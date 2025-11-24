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
                            # Dodano buy_title
                            "value": "`/balance` `/daily` `/pay` `/richlist`\n`/work` `/shop` `/rob`\n`/buy_title` - Prestige titles",
                            "inline": False
                        },
{
                            "name": "🎉 Fun Module",
                            # Dodano blackjack i duel
                            "value": "`/poker` `/blackjack` `/roulette`\n`/duel` - Challenge player\n`/coinflip` `/slots` `/cat`",
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