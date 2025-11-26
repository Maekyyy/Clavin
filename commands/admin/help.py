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
                            "value": "`/balance` `/daily` `/pay` `/richlist`\n`/work` `/contract` `/shop` `/rob`\n`/buy_title` `/crypto`",
                            "inline": False
                        },
                        {
                            "name": "🎰 Casino & Games",
                            "value": "`/poker` `/blackjack` `/roulette`\n`/tictactoe` - Play Tic Tac Toe\n`/slots` `/coinflip` `/duel`",
                            "inline": False
                        },
                        {
                            "name": "🏆 Fun & Social",
                            "value": "`achievements` - Check badges\n`gift` - Give items\n`profile` `rank` `marry`",
                            "inline": False
                        },
                        {
                            "name": "📈 Levels",
                            "value": "`/rank` - Check Level\n`/leaderboard` - XP Ranking",
                            "inline": False
                        },
                    {
                            "name": "⚙️ Utility & System",
                            "value": "`/ask` - AI Chat\n`/weather` - Weather\n`/poll` - Create poll\n`/stats` - Bot status\n`/reset` `/synctest` `/help`",
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