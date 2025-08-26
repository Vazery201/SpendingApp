import os
from cryptography.fernet import Fernet

_key = os.getenv("ENCRYPTION_KEY")
if not _key:
    raise RuntimeError("ENCRYPTION_KEY missing in .env")
# Fernet keys are URL-safe base64-encoded strings. The cryptography
# library expects the key as bytes, so always encode the environment
# variable rather than attempting to detect its format. Previously the
# code skipped encoding when the key began with "gAAAA", which could
# result in a `TypeError` if a valid key happened to have that prefix.
fernet = Fernet(_key.encode())

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
