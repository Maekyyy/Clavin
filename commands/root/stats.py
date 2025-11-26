import time
from database import get_global_stats

STATS_DATA = {
    "name": "stats",
    "description": "Show bot economy statistics & ping",
    "type": 1
}

def cmd_stats(data):
    # 1. Mierzymy czas (Ping bazy danych)
    start_time = time.time()
    
    # 2. Pobieramy dane z bazy
    user_count, total_money = get_global_stats()
    
    end_time = time.time()
    ping = int((end_time - start_time) * 1000) # ms

    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "📊 Clavin Network Stats",
                "color": 0x2ecc71, # Zielony
                "fields": [
                    {
                        "name": "👥 Registered Users",
                        "value": f"**{user_count}** players",
                        "inline": True
                    },
                    {
                        "name": "📡 Latency",
                        "value": f"**{ping}ms**",
                        "inline": True
                    },
                    {
                        "name": "💰 Total Economy (Inflation)",
                        "value": f"**${total_money:,}**",
                        "inline": False
                    },
                    {
                        "name": "⚙️ System",
                        "value": "Google Cloud Run (Serverless)",
                        "inline": False
                    },
                    {
                        "name": "💾 Database", 
                        "value": "Firestore (NoSQL)", 
                        "inline": True
                    },
                    {
                        "name": "🐍 Python Version", 
                        "value": python_v, 
                        "inline": True
                    },
                ],
                "footer": {"text": "Economy Statistics"}
            }]
        }
    }