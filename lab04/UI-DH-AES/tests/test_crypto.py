from crypto.dh_aes import (
    create_parameters,
    create_key_pair,
    derive_shared_secret,
    derive_aes_key,
    encrypt_message,
    decrypt_message,
)


def test_both_sides_derive_same_shared_secret():
    parameters = create_parameters()
    server_private, server_public = create_key_pair(parameters)
    client_private, client_public = create_key_pair(parameters)

    server_secret = derive_shared_secret(server_private, client_public)
    client_secret = derive_shared_secret(client_private, server_public)

    assert server_secret == client_secret
    assert derive_aes_key(server_secret) == derive_aes_key(client_secret)


def test_aes_encrypt_decrypt_round_trip():
    parameters = create_parameters()
    first_private, _first_public = create_key_pair(parameters)
    second_private, second_public = create_key_pair(parameters)
    aes_key = derive_aes_key(derive_shared_secret(first_private, second_public))

    encrypted_payload = encrypt_message(aes_key, "Bao mat")
    plaintext = decrypt_message(aes_key, encrypted_payload)

    assert plaintext == "Bao mat"
