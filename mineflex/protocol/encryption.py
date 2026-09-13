"""AES-128-CFB8 stream encryption for Minecraft protocol."""

from __future__ import annotations

import warnings

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

try:
    from cryptography.hazmat.decrepit.ciphers import modes as decrepit_modes

    CFB8 = decrepit_modes.CFB8
except ImportError:
    from cryptography.hazmat.primitives.ciphers import modes

    CFB8 = modes.CFB8


class EncryptionCipher:
    """Stream cipher wrapper for Minecraft protocol AES-128-CFB8 encryption and decryption."""

    def __init__(self, secret: bytes) -> None:
        self.secret = secret
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._encryptor = Cipher(algorithms.AES(secret), CFB8(secret)).encryptor()
            self._decryptor = Cipher(algorithms.AES(secret), CFB8(secret)).decryptor()

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt bytes using AES-128-CFB8."""
        return self._encryptor.update(data)

    def decrypt(self, data: bytes) -> bytes:
        """Decrypt bytes using AES-128-CFB8."""
        return self._decryptor.update(data)
