import importlib
import os
import sys

# Ensure the backend app package is importable
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


def test_encrypt_decrypt_with_gAAAA_key(monkeypatch):
    key = "gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    monkeypatch.setenv("ENCRYPTION_KEY", key)
    # Reload the crypto module so it picks up the new env var
    crypto = importlib.import_module("app.crypto")
    importlib.reload(crypto)
    token = crypto.encrypt("secret")
    assert crypto.decrypt(token) == "secret"
