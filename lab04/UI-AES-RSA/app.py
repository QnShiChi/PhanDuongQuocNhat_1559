from datetime import datetime

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from crypto.rsa_aes import (
    create_aes_key,
    create_rsa_keypair,
    decrypt_aes_key_with_rsa,
    encrypt_aes_key_with_rsa,
    encrypt_message,
    export_public_key_pem,
)


app = Flask(__name__)
app.config["SECRET_KEY"] = "ui-aes-rsa-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

server_private_key, server_public_key = create_rsa_keypair()
client_sessions = {}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def handle_join(data):
    display_name = (data.get("display_name") or "").strip()
    if not display_name:
        emit("handshake_status", {"level": "error", "message": "Tên hiển thị không hợp lệ"})
        return

    sid = request.sid
    client_sessions[sid] = {
        "display_name": display_name,
        "aes_key": None,
        "ready": False,
    }

    emit("server_public_key", {"public_key_pem": export_public_key_pem(server_public_key)})
    emit("handshake_status", {"level": "info", "message": "Đã nhận RSA public key từ server"})
    emit_online_users()


@socketio.on("request_secure_session")
def handle_request_secure_session(_data):
    sid = request.sid
    session = client_sessions.get(sid)
    if session is None:
        emit("handshake_status", {"level": "error", "message": "Phiên kết nối không tồn tại"})
        return

    aes_key = create_aes_key()
    encrypted_key = encrypt_aes_key_with_rsa(server_public_key, aes_key)
    session["aes_key"] = decrypt_aes_key_with_rsa(server_private_key, encrypted_key)
    session["ready"] = True

    emit("handshake_status", {"level": "success", "message": "Handshake AES-RSA thành công"})
    socketio.emit("system_message", {"message": f"{session['display_name']} đã vào phòng chat"})


@socketio.on("send_message")
def handle_send_message(data):
    sid = request.sid
    session = client_sessions.get(sid)
    if session is None or not session["ready"]:
        emit("handshake_status", {"level": "error", "message": "Phiên mã hóa chưa sẵn sàng"})
        return

    plaintext = (data.get("plaintext") or "").strip()
    if not plaintext:
        emit("handshake_status", {"level": "error", "message": "Tin nhắn rỗng không hợp lệ"})
        return

    timestamp = datetime.now().strftime("%H:%M:%S")
    for target_sid, target_session in client_sessions.items():
        if not target_session["ready"]:
            continue
        encrypted_payload = encrypt_message(target_session["aes_key"], plaintext)
        socketio.emit(
            "new_message",
            {
                "sender": session["display_name"],
                "plaintext": plaintext,
                "timestamp": timestamp,
                "ciphertext": encrypted_payload["ciphertext"],
                "iv": encrypted_payload["iv"],
            },
            to=target_sid,
        )


@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    session = client_sessions.pop(sid, None)
    if session is None:
        return

    socketio.emit("system_message", {"message": f"{session['display_name']} đã rời phòng chat"})
    emit_online_users()


def emit_online_users():
    socketio.emit(
        "online_users",
        {"users": [item["display_name"] for item in client_sessions.values()]},
    )


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5005, debug=True)
