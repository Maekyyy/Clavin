import os
from flask import Flask, jsonify, request
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# IMPORTUJEMY FUNKCJE Z TWOJEGO NOWEGO FOLDERU
from commands.general import cmd_hello, cmd_synctest

app = Flask(__name__)
PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

# TUTAJ REJESTRUJEMY KOMENDY
COMMAND_HANDLERS = {
    "hello": cmd_hello,
    "synctest": cmd_synctest,
}

def verify_signature(request):
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')
    if not signature or not timestamp:
        raise BadSignatureError("Brak nagłówków")
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))

@app.route('/', methods=['POST'])
def interactions():
    try:
        verify_signature(request)
    except Exception:
        return "Invalid signature", 401

    r = request.json

    if r["type"] == 1:
        return jsonify({"type": 1})

    if r["type"] == 2:
        command_name = r["data"]["name"]
        
        if command_name in COMMAND_HANDLERS:
            # Przekazujemy sterowanie do funkcji z folderu commands/
            return jsonify(COMMAND_HANDLERS[command_name](r["data"]))
        else:
            return jsonify({
                "type": 4,
                "data": {"content": "❌ Nieznana komenda."}
            })

    return jsonify({"error": "unknown type"}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))