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
                            "name": "💰 Economy & RPG",
                            "value": "`/balance` `/daily` `/pay` `/richlist`\n`/work` `/shop` `/rob` `/buy_title` `/crypto`",
                            "inline": False
                        },
                        {
                            "name": "🎰 Casino & Games",
                            "value": "`/poker` `/blackjack` `/roulette`\n`/slots` `/coinflip` `/duel`",
                            "inline": False
                        },
                        {
                            "name": "🎉 Fun & Social",
                            # Dodano tutaj roll i meme:
                            "value": "`/meme` - Generator memów\n`/roll` - Rzut kośćmi (RPG)\n`/ship` `/avatar` `/cat` `/8ball` `/hello`",
                            "inline": False
                        },
                        {
                            "name": "📈 Levels",
                            "value": "`/rank` - Check Level\n`/leaderboard` - XP Ranking",
                            "inline": False
                        },
                        {
                            "name": "⚙️ Utility & System",
                            # Dodano ask (AI) i poll
                            "value": "`/ask` - Chat with AI\n`/poll` - Create poll\n`/serverinfo` `/synctest` `/help`",
                            "inline": False
                        },
                        {
                            "name": "🛡️ Admin",
                            "value": "`/clear` `/kick` `/ban`",
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