SYNCTEST_DATA = {
    "name": "synctest",
    "description": "Test połączenia (Module Root)",
    "type": 1
}

def cmd_synctest(data):
    return {
        "type": 4,
        "data": {
            "content": "✅ **System Root:** Połączenie stabilne. Moduły załadowane."
        }
    }