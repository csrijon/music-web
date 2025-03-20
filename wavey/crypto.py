import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES



def generate_aes_cipher() -> Cipher:
    """Generate AES cipher"""
    aes_key = os.environ["AES_KEY_32"]
    return Cipher(algorithms.AES(aes_key.encode()), modes.CFB8(b"\x00" * 16))


def encrypt(data: bytes) -> str:
    """Encrypt data using AES"""
    encryptor = generate_aes_cipher().encryptor()
    ct = encryptor.update(data) + encryptor.finalize()
    return ct.hex()


def decrypt(data: bytes) -> str:
    """Decrypt AES encrypted data"""
    dec = generate_aes_cipher().decryptor()
    pt = dec.update(data) + dec.finalize()
    return pt.decode()


def b64_decrypt(emu: str) -> bytes:
    """Decrypt base64 encoded data using TripleDES"""
    url = base64.b64decode(emu)
    cipher = Cipher(TripleDES(b"38346591"), modes.ECB())
    dec = cipher.decryptor()
    return dec.update(url) + dec.finalize()
