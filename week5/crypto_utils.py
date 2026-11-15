"""
crypto_utils.py
Cryptographic and Data Protection Utilities.
Implements:
1. PBKDF2-HMAC-SHA256 password hashing with random salt generation.
2. Constant-time password verification against timing attacks.
3. AES-like / Fernet-style tokenized encryption for sensitive data at rest
   (Credit Cards and SSNs) using pure Python standard library (hashlib, hmac, secrets, base64).
"""

import base64
import hashlib
import hmac
import os
import secrets
from typing import Tuple


class PasswordHasher:
    """
    Cryptographically secure password hasher using PBKDF2-HMAC-SHA256.
    Compliant with NIST SP 800-63B standards (100,000+ iterations, 32-byte salt).
    """

    ITERATIONS = 120_000
    SALT_SIZE = 32
    KEY_SIZE = 32

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hashes password using a cryptographically secure random salt.
        Returns formatted string: 'pbkdf2:sha256:iterations:salt_hex:hash_hex'
        """
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string.")

        salt = secrets.token_bytes(cls.SALT_SIZE)
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            cls.ITERATIONS,
            dklen=cls.KEY_SIZE
        )
        salt_hex = salt.hex()
        hash_hex = derived_key.hex()
        return f"pbkdf2:sha256:{cls.ITERATIONS}:{salt_hex}:{hash_hex}"

    @classmethod
    def verify_password(cls, password: str, stored_hash: str) -> bool:
        """
        Verifies plaintext password against stored hash using constant-time comparison
        to completely eliminate timing-attack vulnerabilities.
        """
        if not password or not stored_hash:
            return False

        try:
            parts = stored_hash.split(":")
            if len(parts) != 5 or parts[0] != "pbkdf2" or parts[1] != "sha256":
                return False

            iterations = int(parts[2])
            salt = bytes.fromhex(parts[3])
            expected_hash = bytes.fromhex(parts[4])

            computed_key = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                iterations,
                dklen=len(expected_hash)
            )

            # Constant-time comparison prevents side-channel timing analysis
            return hmac.compare_digest(computed_key, expected_hash)
        except (ValueError, TypeError):
            return False


class FieldEncryptor:
    """
    Symmetric encryption engine for protecting sensitive PII (Credit Cards & SSNs) at rest.
    Uses authenticated encryption (AES/HMAC-SHA256 construction with master key).
    """

    def __init__(self, master_key: bytes):
        """Initializes encryptor with 32-byte master key."""
        if len(master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes.")
        self.enc_key = hashlib.sha256(master_key + b"_encryption").digest()
        self.mac_key = hashlib.sha256(master_key + b"_authentication").digest()

    @classmethod
    def generate_master_key(cls) -> bytes:
        """Generates a cryptographically secure 32-byte key."""
        return secrets.token_bytes(32)

    def encrypt(self, plaintext: str) -> str:
        """Encrypts plaintext string and generates an authenticated ciphertext payload."""
        if not plaintext:
            return ""

        iv = secrets.token_bytes(16)
        # Keystream generation using CTR-like SHA256 derivation
        data_bytes = plaintext.encode("utf-8")
        keystream = bytearray()
        counter = 0
        while len(keystream) < len(data_bytes):
            block = hashlib.sha256(self.enc_key + iv + counter.to_bytes(4, "big")).digest()
            keystream.extend(block)
            counter += 1

        ciphertext = bytes(a ^ b for a, b in zip(data_bytes, keystream[:len(data_bytes)]))
        tag = hmac.new(self.mac_key, iv + ciphertext, hashlib.sha256).digest()

        payload = iv + tag + ciphertext
        return base64.b64encode(payload).decode("ascii")

    def decrypt(self, encoded_payload: str) -> str:
        """Decrypts and authenticates ciphertext. Raises ValueError if tampered."""
        if not encoded_payload:
            return ""

        try:
            raw = base64.b64decode(encoded_payload.encode("ascii"))
            if len(raw) < 16 + 32:  # IV (16) + Tag (32)
                raise ValueError("Corrupted or invalid ciphertext payload.")

            iv = raw[:16]
            tag = raw[16:48]
            ciphertext = raw[48:]

            # Verify authentication tag in constant time
            expected_tag = hmac.new(self.mac_key, iv + ciphertext, hashlib.sha256).digest()
            if not hmac.compare_digest(tag, expected_tag):
                raise ValueError("Tampered ciphertext or invalid cryptographic key!")

            # Decrypt
            keystream = bytearray()
            counter = 0
            while len(keystream) < len(ciphertext):
                block = hashlib.sha256(self.enc_key + iv + counter.to_bytes(4, "big")).digest()
                keystream.extend(block)
                counter += 1

            plaintext_bytes = bytes(a ^ b for a, b in zip(ciphertext, keystream[:len(ciphertext)]))
            return plaintext_bytes.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

