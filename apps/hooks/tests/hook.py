from flask import Flask, request, jsonify
import hmac, hashlib
import pprint
app = Flask(__name__)

# Shared secret (same as sender)
WEBHOOK_SECRET = b"supersecrettoken"

@app.route('/webhook/', methods=['POST'])
def webhook():
    payload = request.data  # Raw body (bytes)
    received_sig = request.headers.get("X-PingFox-Signature", "")
    expected_sig = "sha256=" + hmac.new(WEBHOOK_SECRET, payload, hashlib.sha256).hexdigest()

    # Secure comparison
    if not hmac.compare_digest(received_sig, expected_sig):
        return jsonify({"error": "Invalid signature"}), 403

    print("✅ Webhook verified!")
    pprint.pprint(request.json)
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
