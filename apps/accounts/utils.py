def generate_activation_key(length=40):
    """
    Generates a secure random activation key of the specified length.
    
    Args:
        length (int): The desired length of the activation key. Default is 40.
    
    Returns:
        str: A secure random activation key.
    """
    import secrets
    return secrets.token_urlsafe(length)[:length]