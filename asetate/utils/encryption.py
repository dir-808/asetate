"""Encryption utilities for sensitive data like API tokens."""

import base64
import os

from cryptography.fernet import Fernet
from flask import current_app


def get_encryption_key() -> bytes:
    """Get or derive encryption key from SECRET_KEY.

    Uses the app's SECRET_KEY to derive a Fernet-compatible key.
    The SECRET_KEY must be at least 32 characters for security.
    """
    secret_key = current_app.config.get("SECRET_KEY", "")
    if not secret_key or len(secret_key) < 32:
        raise ValueError(
            "SECRET_KEY must be at least 32 characters for encryption. "
            "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )

    # Derive a 32-byte key from SECRET_KEY using first 32 bytes
    key_bytes = secret_key.encode()[:32]
    # Pad if needed (shouldn't happen with proper key)
    key_bytes = key_bytes.ljust(32, b'\0')
    # Fernet requires base64-encoded 32-byte key
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_token(token: str) -> str:
    """Encrypt a token for secure storage.

    Args:
        token: The plaintext token to encrypt

    Returns:
        Base64-encoded encrypted token
    """
    if not token:
        return ""

    key = get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a stored token.

    Args:
        encrypted_token: Base64-encoded encrypted token

    Returns:
        The decrypted plaintext token
    """
    if not encrypted_token:
        return ""

    try:
        key = get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_token.encode())
        return decrypted.decode()
    except Exception:
        # If decryption fails (key changed, corrupted data), return empty
        return ""
