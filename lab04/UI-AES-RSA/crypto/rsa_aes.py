import base64

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def create_rsa_keypair():
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    return private_key, public_key


def export_public_key_pem(public_key):
    return public_key.export_key().decode("utf-8")


def load_public_key_pem(public_key_pem):
    return RSA.import_key(public_key_pem.encode("utf-8"))


def create_aes_key():
    return get_random_bytes(16)


def encrypt_aes_key_with_rsa(public_key, aes_key):
    cipher = PKCS1_OAEP.new(public_key)
    encrypted_key = cipher.encrypt(aes_key)
    return base64.b64encode(encrypted_key).decode("utf-8")


def decrypt_aes_key_with_rsa(private_key, encrypted_key_b64):
    cipher = PKCS1_OAEP.new(private_key)
    encrypted_key = base64.b64decode(encrypted_key_b64.encode("utf-8"))
    return cipher.decrypt(encrypted_key)


def encrypt_message(aes_key, plaintext):
    cipher = AES.new(aes_key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))
    return {
        "iv": base64.b64encode(cipher.iv).decode("utf-8"),
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
    }


def decrypt_message(aes_key, payload):
    iv = base64.b64decode(payload["iv"].encode("utf-8"))
    ciphertext = base64.b64decode(payload["ciphertext"].encode("utf-8"))
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode("utf-8")
