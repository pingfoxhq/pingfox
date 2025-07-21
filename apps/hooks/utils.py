import hmac, hashlib

def generate_webhook_signature(secret, payload):
    """
    Generate a HMAC signature for the given payload using the provided secret.
    """
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()