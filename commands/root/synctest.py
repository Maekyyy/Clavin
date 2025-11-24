SYNCTEST_DATA = {
    "name": "synctest",
    "description": "Connection test (Root Module)",
    "type": 1
}

def cmd_synctest(data):
    return {
        "type": 4,
        "data": {
            "content": "✅ **System Root:** Connection stable. Modules loaded."
        }
    }