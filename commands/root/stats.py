import sys
import platform

STATS_DATA = {
    "name": "stats",
    "description": "Show bot system statistics",
    "type": 1
}

def cmd_stats(data):
    python_v = sys.version.split()[0]
    system = platform.system()
    
    return {
        "type": 4,
        "data": {
            "embeds": [{
                "title": "📊 Clavin Bot Statistics",
                "color": 0x3498db,
                "fields": [
                    {"name": "🐍 Python Version", "value": python_v, "inline": True},
                    {"name": "☁️ Hosting", "value": "Google Cloud Run", "inline": True},
                    {"name": "🟢 Architecture", "value": "Serverless (Stateless)", "inline": False},
                    {"name": "💾 Database", "value": "Firestore (NoSQL)", "inline": True}
                ],
                "footer": {"text": "Clavin v3.0"}
            }]
        }
    }