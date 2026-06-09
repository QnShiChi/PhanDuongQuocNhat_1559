from app import app, socketio


def test_join_returns_server_public_key():
    client = socketio.test_client(app, flask_test_client=app.test_client())

    client.emit("join", {"display_name": "An"})
    received = client.get_received()

    event_names = [item["name"] for item in received]
    assert "server_dh_public_key" in event_names
    assert "handshake_status" in event_names
    assert "online_users" in event_names


def test_message_is_relayed_to_other_clients_after_handshake():
    first = socketio.test_client(app, flask_test_client=app.test_client())
    second = socketio.test_client(app, flask_test_client=app.test_client())

    first.emit("join", {"display_name": "An"})
    second.emit("join", {"display_name": "Binh"})

    first_payload = first.get_received()
    second_payload = second.get_received()

    first_public_key = next(
        item["args"][0]["public_key_pem"]
        for item in first_payload
        if item["name"] == "server_dh_public_key"
    )
    second_public_key = next(
        item["args"][0]["public_key_pem"]
        for item in second_payload
        if item["name"] == "server_dh_public_key"
    )

    first.emit("request_secure_session", {"server_public_key_pem": first_public_key})
    second.emit("request_secure_session", {"server_public_key_pem": second_public_key})
    first.get_received()
    second.get_received()

    first.emit("send_message", {"plaintext": "Xin chao"})
    received = second.get_received()

    assert any(
        item["name"] == "new_message" and item["args"][0]["plaintext"] == "Xin chao"
        for item in received
    )
    assert any(
        item["name"] == "new_message" and "ciphertext" in item["args"][0]
        for item in received
    )
