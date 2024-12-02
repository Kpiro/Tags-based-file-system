import hashlib

def calculate_hash(value : str, m):
    """Calcula el hash de una clave usando SHA-1."""
    return int(hashlib.sha1(value.encode('utf-8')).hexdigest(), 16) % (2**m)