from datetime import datetime

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from crypto.dh_aes import (
    create_key_pair,
    create_parameters,
    derive_aes_key,
    derive_shared_secret,
    encrypt_message,
    export_public_key_pem,
    load_public_key_pem,
)


app = Flask(__name__)
app.config["SECRET_KEY"] = "ui-dh-aes-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

parameters = create_parameters()
server_private_key, server_public_key = create_key_pair(parameters)
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

    emit("server_dh_public_key", {"public_key_pem": export_public_key_pem(server_public_key)})
    emit("handshake_status", {"level": "info", "message": "Đã nhận DH public key của server"})
    emit_online_users()


@socketio.on("request_secure_session")
def handle_request_secure_session(data):
    sid = request.sid
    session = client_sessions.get(sid)
    if session is None:
        emit("handshake_status", {"level": "error", "message": "Phiên kết nối không tồn tại"})
        return

    server_public_key_pem = data.get("server_public_key_pem")
    if not server_public_key_pem:
        emit("handshake_status", {"level": "error", "message": "Thiếu DH public key của server"})
        return

    public_key = load_public_key_pem(server_public_key_pem)
    client_private_key, client_public_key = create_key_pair(parameters)
    client_secret = derive_shared_secret(client_private_key, public_key)
    server_secret = derive_shared_secret(server_private_key, client_public_key)

    if client_secret != server_secret:
        emit("handshake_status", {"level": "error", "message": "Không thể tạo shared secret"})
        return

    session["aes_key"] = derive_aes_key(server_secret)
    session["ready"] = True
    emit("handshake_status", {"level": "success", "message": "Handshake Diffie-Hellman thành công"})
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
                "ciphertext": encrypted_payload["ciphertext"],
                "iv": encrypted_payload["iv"],
                "timestamp": timestamp,
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
    socketio.run(app, host="127.0.0.1", port=5001, debug=True)
