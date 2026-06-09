from app import app, socketio


def test_join_returns_public_key_and_online_users():
    client = socketio.test_client(app, flask_test_client=app.test_client())

    client.emit("join", {"display_name": "An"})
    received = client.get_received()

    event_names = [item["name"] for item in received]
    assert "server_public_key" in event_names
    assert "handshake_status" in event_names
    assert "online_users" in event_names


def test_message_is_relayed_to_other_clients():
    first = socketio.test_client(app, flask_test_client=app.test_client())
    second = socketio.test_client(app, flask_test_client=app.test_client())

    first.emit("join", {"display_name": "An"})
    second.emit("join", {"display_name": "Binh"})

    first.get_received()
    second.get_received()

    first.emit("request_secure_session", {})
    second.emit("request_secure_session", {})
    first.get_received()
    second.get_received()

    first.emit("send_message", {"plaintext": "Chao ban"})

    received = second.get_received()
    assert any(
        item["name"] == "new_message" and item["args"][0]["plaintext"] == "Chao ban"
        for item in received
    )
    assert any(
        item["name"] == "new_message" and "ciphertext" in item["args"][0]
        for item in received
    )
