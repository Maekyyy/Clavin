HELP_DATA = {
    "name": "help",
    "description": "Wyświetla listę dostępnych komend",
    "type": 1
}

def cmd_help(data):
    return {
        "type": 4,
        "data": {
            "embeds": [
                {
                    "title": "📜 Lista Komend Clavin Bot",
                    "description": "Oto spis wszystkich funkcji dostępnych w bocie:",
                    "color": 0x3498db,  # Niebieski kolor
                    "fields": [
                        {
                            "name": "🎉 Moduł Fun",
                            "value": "`/hello` - Przywitanie z botem",
                            "inline": False
                        },
                        {
                            "name": "⚙️ Moduł Root",
                            "value": "`/synctest` - Sprawdzenie stanu połączenia",
                            "inline": False
                        },
                        {
                            "name": "🛡️ Moduł Admin",
                            "value": "`/serverinfo` - Informacje o serwerze\n`/help` - Wyświetla tę listę",
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": "Działam na Google Cloud Run"
                    }
                }
            ]
        }
    }