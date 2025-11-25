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
                    "color": 0x3498db,
                    "fields": [
                        {
                            "name": "💰 Economy & GTA",
                            "value": "`/balance` `/daily` `/pay` `/richlist`\n`/crime` - High risk cash\n`/businesses` - Manage empire\n`/buy_business` - Buy factory\n`/launder` - Collect income\n`/shop` - Items & Titles",
                            "inline": False
                        },
                        {
                            "name": "🎰 Casino & Games",
                            "value": "`poker` - Video Poker\n`blackjack` - Classic 21\n`roulette` - Casino Roulette\n`slots` - Slot Machine\n`coinflip` - Heads or Tails\n`duel` - Challenge a player",
                            "inline": False
                        },
                        {
                            "name": "🎉 Fun Module",
                            "value": "`/ask` - Chat with AI 🧠\n`/poker` `/blackjack` `/roulette`\n`/coinflip` `/slots` `/cat`",
                            "inline": False
                        },
                        {
                            "name": "📈 Levels",
                            "value": "`rank` - Check Level\n`leaderboard` - XP Ranking",
                            "inline": False
                        },
                        {
                            "name": "🛡️ Admin & Moderation",
                            "value": "`/serverinfo` - Server stats\n`/clear` - Delete messages\n`/kick` - Kick user\n`/ban` - Ban user\n`/help` - Show commands",
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