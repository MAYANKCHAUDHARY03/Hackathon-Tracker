import os
from cryptography.fernet import Fernet
import json
from typing import Dict, Any

# In production, this should be an environment variable. 
# For now, we generate one if not present, but for persistent DB we need a fixed key.
# We will use a dummy static key for demonstration of the vault, 
# but warn that it must be set via env in real prod.
VAULT_KEY = os.getenv("VAULT_SECRET_KEY", "uNq8L9oN2P4R_q8uS2bY3H8iJ5xZ7vK0aX1wY2bQ3jU=") 
_fernet = Fernet(VAULT_KEY.encode('utf-8'))

def encrypt_dict(data: Dict[str, Any]) -> str:
    """Encrypts a dictionary into a secure token."""
    json_data = json.dumps(data)
    encrypted = _fernet.encrypt(json_data.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_dict(token: str) -> Dict[str, Any]:
    """Decrypts a secure token back to a dictionary."""
    if not token:
        return {}
    decrypted = _fernet.decrypt(token.encode('utf-8'))
    return json.loads(decrypted.decode('utf-8'))

def encrypt_string(data: str) -> str:
    if not data:
        return data
    encrypted = _fernet.encrypt(data.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_string(token: str) -> str:
    if not token:
        return token
    decrypted = _fernet.decrypt(token.encode('utf-8'))
    return decrypted.decode('utf-8')
