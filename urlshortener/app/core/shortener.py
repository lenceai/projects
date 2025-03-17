import string
import random

ALPHABET = string.ascii_letters + string.digits
BASE = len(ALPHABET)

def encode_base62(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    
    arr = []
    while num:
        num, rem = divmod(num, BASE)
        arr.append(ALPHABET[rem])
    arr.reverse()
    return ''.join(arr)

def generate_short_key(length: int = 6) -> str:
    """Generate a random short key."""
    return ''.join(random.choices(ALPHABET, k=length))

def create_unique_short_key(db, URL, length: int = 6) -> str:
    """Create a unique short key that doesn't exist in the database."""
    while True:
        short_key = generate_short_key(length)
        exists = db.query(URL).filter(URL.short_key == short_key).first()
        if not exists:
            return short_key 