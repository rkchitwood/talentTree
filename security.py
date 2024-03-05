import secrets, string
from datetime import datetime, timedelta

TOKEN_LENGTH = 50
TOKEN_EXPIRATION = timedelta(hours=24)

def generate_token(length=TOKEN_LENGTH):
    """Generate a random token."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def calculate_expiration():
    """Calculate the expiration time for a token."""
    return datetime.now() + TOKEN_EXPIRATION