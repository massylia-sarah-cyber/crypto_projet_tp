import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


AES_KEY_SIZE = 32
NONCE_SIZE = 12


def generate_aes_key() -> bytes:
    return os.urandom(AES_KEY_SIZE)


def aes_encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce, ciphertext


def aes_decrypt(nonce: bytes, ciphertext: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)
