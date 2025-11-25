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
                            "name": "💰 Economy & RPG",
                            "value": "`balance` `daily` `pay` `richlist`\n`work` `shop` `rob`\n`buy_title` `crypto`",
                            "inline": False
                        },
                        {
                            "name": "🎰 Casino & Games",
                            "value": "`poker` - Video Poker\n`blackjack` - Classic 21\n`roulette` - Casino Roulette\n`slots` - Slot Machine\n`coinflip` - Heads or Tails\n`duel` - Challenge a player",
                            "inline": False
                        },
                        {
                            "name": "🎉 Fun & Social",
                            "value": "`cat` `hello` `8ball`\n`ship` - Love Calculator\n`avatar` - Get User Picture",
                            "inline": False
                        },
                        {
                            "name": "📈 Levels",
                            "value": "`rank` - Check Level\n`leaderboard` - XP Ranking",
                            "inline": False
                        },
                        {
                            "name": "⚙️ System",
                            "value": "`serverinfo` `synctest` `help`",
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