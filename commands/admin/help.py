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
                            # Usunąłem buy_title (jest w shop), dodałem crypto
                            "value": "`/balance` `/daily` `/pay` `/richlist`\n`/work` `/shop` `/rob` `/crypto`",
                            "inline": False
                        },
                        {
                            "name": "🎰 Casino & Games",
                            "value": "`/poker` `/blackjack` `/roulette`\n`/slots` `/coinflip` `/duel`",
                            "inline": False
                        },
                        {
                            "name": "🎉 Fun & Social",
                            # Poprawione opisy na angielski
                            "value": "`/meme` - Meme Generator\n`/roll` - Dice Roll (RPG)\n`/ship` `/avatar` `/cat` `/8ball` `/hello`",
                            "inline": False
                        },
                        {
                            "name": "📈 Levels",
                            "value": "`/rank` - Check Level\n`/leaderboard` - XP Ranking",
                            "inline": False
                        },
                        {
                            "name": "⚙️ Utility & System",
                            # Dodano weather i reset
                            "value": "`/ask` - Chat with AI\n`/weather` - Check weather\n`/poll` - Create poll\n`/reset` - Fix stuck game\n`/serverinfo` `/synctest` `/help`",
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