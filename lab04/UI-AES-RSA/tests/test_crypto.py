from crypto.rsa_aes import (
    create_rsa_keypair,
    create_aes_key,
    encrypt_aes_key_with_rsa,
    decrypt_aes_key_with_rsa,
    encrypt_message,
    decrypt_message,
)


def test_rsa_wraps_and_unwraps_aes_key():
    private_key, public_key = create_rsa_keypair()
    aes_key = create_aes_key()

    encrypted_key = encrypt_aes_key_with_rsa(public_key, aes_key)
    decrypted_key = decrypt_aes_key_with_rsa(private_key, encrypted_key)

    assert decrypted_key == aes_key


def test_aes_encrypt_decrypt_round_trip():
    aes_key = create_aes_key()

    encrypted_payload = encrypt_message(aes_key, "Xin chao")
    plaintext = decrypt_message(aes_key, encrypted_payload)

    assert plaintext == "Xin chao"
    assert encrypted_payload["ciphertext"] != "Xin chao"
