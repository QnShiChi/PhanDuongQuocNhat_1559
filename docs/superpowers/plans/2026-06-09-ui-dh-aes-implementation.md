# UI-DH-AES Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained web app in `lab04/UI-DH-AES` that demonstrates multi-client secure chat through a server using Diffie-Hellman key exchange to derive AES session keys.

**Architecture:** Use one Flask application to serve the Bootstrap UI and host Socket.IO events for realtime chat. Isolate Diffie-Hellman and AES helpers into a dedicated crypto module, then keep app state in a session registry keyed by Socket.IO session id.

**Tech Stack:** Python, Flask, Flask-SocketIO, cryptography, HTML, Bootstrap 5, vanilla JavaScript, pytest

---

## File Structure

- Create: `lab04/UI-DH-AES/app.py` - Flask app, Socket.IO handlers, per-client handshake state
- Create: `lab04/UI-DH-AES/requirements.txt` - runtime dependencies
- Create: `lab04/UI-DH-AES/crypto/__init__.py` - crypto package marker
- Create: `lab04/UI-DH-AES/crypto/dh_aes.py` - DH key generation, shared secret derivation, AES helpers
- Create: `lab04/UI-DH-AES/templates/index.html` - single-page Bootstrap UI
- Create: `lab04/UI-DH-AES/static/css/styles.css` - layout polish
- Create: `lab04/UI-DH-AES/static/js/app.js` - Socket.IO client and DOM updates
- Create: `lab04/UI-DH-AES/tests/test_crypto.py` - DH/AES helper tests
- Create: `lab04/UI-DH-AES/tests/test_app.py` - handshake and relay tests

### Task 1: Scaffold Project Files

**Files:**
- Create: `lab04/UI-DH-AES/requirements.txt`
- Create: `lab04/UI-DH-AES/crypto/__init__.py`

- [ ] **Step 1: Create dependency manifest**

```text
Flask==3.0.3
Flask-SocketIO==5.3.6
python-socketio==5.11.4
eventlet==0.36.1
cryptography==42.0.8
pytest==8.2.2
```

- [ ] **Step 2: Create crypto package marker**

```python
# lab04/UI-DH-AES/crypto/__init__.py
```

- [ ] **Step 3: Verify files exist**

Run: `Get-ChildItem lab04\UI-DH-AES -Recurse`
Expected: shows `requirements.txt` and `crypto\__init__.py`

- [ ] **Step 4: Commit**

```bash
git add lab04/UI-DH-AES/requirements.txt lab04/UI-DH-AES/crypto/__init__.py
git commit -m "chore: scaffold ui dh aes project"
```

### Task 2: Write Crypto Tests First

**Files:**
- Test: `lab04/UI-DH-AES/tests/test_crypto.py`

- [ ] **Step 1: Write the failing test**

```python
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
    first_private, first_public = create_key_pair(parameters)
    second_private, second_public = create_key_pair(parameters)
    aes_key = derive_aes_key(derive_shared_secret(first_private, second_public))

    encrypted_payload = encrypt_message(aes_key, "Bao mat")
    plaintext = decrypt_message(aes_key, encrypted_payload)

    assert plaintext == "Bao mat"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest lab04/UI-DH-AES/tests/test_crypto.py -v`
Expected: FAIL with missing `crypto.dh_aes`

- [ ] **Step 3: Commit the failing test**

```bash
git add lab04/UI-DH-AES/tests/test_crypto.py
git commit -m "test: define dh aes crypto expectations"
```

### Task 3: Implement DH/AES Helper Module

**Files:**
- Create: `lab04/UI-DH-AES/crypto/dh_aes.py`

- [ ] **Step 1: Write minimal implementation**

```python
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.padding import PKCS7
import os


def create_parameters():
    return dh.generate_parameters(generator=2, key_size=2048)


def create_key_pair(parameters):
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()
    return private_key, public_key


def export_public_key_pem(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


def load_public_key_pem(public_key_pem):
    return serialization.load_pem_public_key(public_key_pem.encode("utf-8"))


def derive_shared_secret(private_key, peer_public_key):
    return private_key.exchange(peer_public_key)


def derive_aes_key(shared_secret):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ui-dh-aes-chat",
    ).derive(shared_secret)


def encrypt_message(aes_key, plaintext):
    iv = os.urandom(16)
    padder = PKCS7(128).padder()
    padded = padder.update(plaintext.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return {
        "iv": base64.b64encode(iv).decode("utf-8"),
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
    }


def decrypt_message(aes_key, payload):
    iv = base64.b64decode(payload["iv"].encode("utf-8"))
    ciphertext = base64.b64decode(payload["ciphertext"].encode("utf-8"))
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()
    return plaintext.decode("utf-8")
```

- [ ] **Step 2: Run crypto tests**

Run: `pytest lab04/UI-DH-AES/tests/test_crypto.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add lab04/UI-DH-AES/crypto/dh_aes.py
git commit -m "feat: add dh aes crypto helpers"
```

### Task 4: Write Failing Server Tests

**Files:**
- Test: `lab04/UI-DH-AES/tests/test_app.py`

- [ ] **Step 1: Write the failing test**

```python
from app import app, socketio


def test_join_returns_server_public_key():
    client = socketio.test_client(app, flask_test_client=app.test_client())
    client.emit("join", {"display_name": "An"})
    received = client.get_received()
    assert any(item["name"] == "server_dh_public_key" for item in received)


def test_message_is_relayed_to_other_clients_after_handshake():
    first = socketio.test_client(app, flask_test_client=app.test_client())
    second = socketio.test_client(app, flask_test_client=app.test_client())

    first.emit("join", {"display_name": "An"})
    second.emit("join", {"display_name": "Binh"})

    first_payload = first.get_received()
    second_payload = second.get_received()

    first_public_key = next(item["args"][0]["public_key_pem"] for item in first_payload if item["name"] == "server_dh_public_key")
    second_public_key = next(item["args"][0]["public_key_pem"] for item in second_payload if item["name"] == "server_dh_public_key")

    assert first_public_key == second_public_key
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest lab04/UI-DH-AES/tests/test_app.py -v`
Expected: FAIL because `app.py` does not exist yet

- [ ] **Step 3: Commit the failing test**

```bash
git add lab04/UI-DH-AES/tests/test_app.py
git commit -m "test: define ui dh aes server behavior"
```

### Task 5: Implement Flask + Socket.IO Server

**Files:**
- Create: `lab04/UI-DH-AES/app.py`

- [ ] **Step 1: Write minimal implementation**

```python
from datetime import datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from crypto.dh_aes import (
    create_parameters,
    create_key_pair,
    derive_aes_key,
    derive_shared_secret,
    encrypt_message,
    export_public_key_pem,
    load_public_key_pem,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "ui-dh-aes-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

parameters = create_parameters()
server_private_key, server_public_key = create_key_pair(parameters)
client_sessions = {}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def handle_join(data):
    sid = request.sid
    client_sessions[sid] = {
        "display_name": data["display_name"].strip(),
        "aes_key": None,
        "ready": False,
    }
    emit("server_dh_public_key", {"public_key_pem": export_public_key_pem(server_public_key)})
    emit("handshake_status", {"level": "info", "message": "Da nhan DH public key cua server"})
    emit_online_users()


@socketio.on("submit_client_public_key")
def handle_submit_client_public_key(data):
    sid = request.sid
    client_public_key = load_public_key_pem(data["public_key_pem"])
    shared_secret = derive_shared_secret(server_private_key, client_public_key)
    client_sessions[sid]["aes_key"] = derive_aes_key(shared_secret)
    client_sessions[sid]["ready"] = True
    emit("handshake_status", {"level": "success", "message": "Handshake Diffie-Hellman thanh cong"})
    emit("system_message", {"message": f"{client_sessions[sid]['display_name']} da vao phong"}, broadcast=True)


@socketio.on("send_message")
def handle_send_message(data):
    sid = request.sid
    session = client_sessions[sid]
    plaintext = data["plaintext"].strip()
    timestamp = datetime.now().strftime("%H:%M:%S")
    for target_sid, target_session in client_sessions.items():
        if not target_session["ready"]:
            continue
        encrypted_payload = encrypt_message(target_session["aes_key"], plaintext)
        emit(
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
    if session:
        emit("system_message", {"message": f"{session['display_name']} da roi phong"}, broadcast=True)
        emit_online_users()


def emit_online_users():
    emit("online_users", {"users": [item["display_name"] for item in client_sessions.values()]}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5001, debug=True)
```

- [ ] **Step 2: Run server tests**

Run: `pytest lab04/UI-DH-AES/tests/test_app.py -v`
Expected: PASS for public-key handshake behavior, or one targeted failure from payload naming

- [ ] **Step 3: Fix payload names if needed and rerun**

Run: `pytest lab04/UI-DH-AES/tests/test_app.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add lab04/UI-DH-AES/app.py
git commit -m "feat: add ui dh aes socket server"
```

### Task 6: Build Bootstrap UI

**Files:**
- Create: `lab04/UI-DH-AES/templates/index.html`
- Create: `lab04/UI-DH-AES/static/css/styles.css`

- [ ] **Step 1: Create page template**

```html
<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Secure Chat DH-AES</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
  </head>
  <body class="bg-body-tertiary">
    <div class="container py-4">
      <div class="row g-3">
        <div class="col-lg-4">
          <div class="card shadow-sm mb-3">
            <div class="card-body">
              <h1 class="h4">Secure Chat DH-AES</h1>
              <p class="text-muted mb-3">Chat nhieu client qua server voi Diffie-Hellman + AES.</p>
              <div class="mb-3">
                <label for="displayName" class="form-label">Ten hien thi</label>
                <input id="displayName" class="form-control" maxlength="30">
              </div>
              <div class="d-grid gap-2">
                <button id="connectBtn" class="btn btn-primary">Ket noi</button>
                <button id="disconnectBtn" class="btn btn-outline-secondary" disabled>Ngat ket noi</button>
              </div>
            </div>
          </div>
          <div class="card shadow-sm mb-3">
            <div class="card-body">
              <h2 class="h6">Thong tin phien</h2>
              <div id="sessionInfo"></div>
            </div>
          </div>
          <div class="card shadow-sm">
            <div class="card-body">
              <h2 class="h6">Nguoi dang online</h2>
              <ul id="onlineUsers" class="list-group list-group-flush"></ul>
            </div>
          </div>
        </div>
        <div class="col-lg-8">
          <div class="card shadow-sm mb-3">
            <div class="card-body">
              <h2 class="h6">Nhat ky bao mat</h2>
              <div id="securityLog" class="log-panel"></div>
            </div>
          </div>
          <div class="card shadow-sm">
            <div class="card-body">
              <div id="chatMessages" class="chat-panel mb-3"></div>
              <div class="input-group">
                <input id="messageInput" class="form-control" placeholder="Nhap tin nhan" disabled>
                <button id="sendBtn" class="btn btn-success" disabled>Gui</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
  </body>
</html>
```

- [ ] **Step 2: Add minimal styles**

```css
.chat-panel,
.log-panel {
  min-height: 320px;
  max-height: 320px;
  overflow-y: auto;
}

.message-item {
  border-radius: 12px;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
}

.message-self {
  background: #cff4fc;
}

.message-other {
  background: #f8f9fa;
}
```

- [ ] **Step 3: Verify template route loads**

Run: `python lab04/UI-DH-AES/app.py`
Expected: server starts on `http://127.0.0.1:5001`

- [ ] **Step 4: Commit**

```bash
git add lab04/UI-DH-AES/templates/index.html lab04/UI-DH-AES/static/css/styles.css
git commit -m "feat: add ui dh aes bootstrap layout"
```

### Task 7: Implement Browser Client Logic

**Files:**
- Create: `lab04/UI-DH-AES/static/js/app.js`

- [ ] **Step 1: Add client workflow**

```javascript
const socket = io();
const state = { connected: false, displayName: "", ready: false };

const connectBtn = document.getElementById("connectBtn");
const disconnectBtn = document.getElementById("disconnectBtn");
const sendBtn = document.getElementById("sendBtn");
const displayNameInput = document.getElementById("displayName");
const messageInput = document.getElementById("messageInput");
const chatMessages = document.getElementById("chatMessages");
const securityLog = document.getElementById("securityLog");
const onlineUsers = document.getElementById("onlineUsers");
const sessionInfo = document.getElementById("sessionInfo");

function logSecurity(message, level = "secondary") {
  securityLog.insertAdjacentHTML("beforeend", `<div class="alert alert-${level} py-2 mb-2">${message}</div>`);
}

function renderSession() {
  sessionInfo.innerHTML = `
    <p class="mb-1"><strong>Ten:</strong> ${state.displayName || "-"}</p>
    <p class="mb-1"><strong>Trang thai:</strong> ${state.connected ? "Da ket noi" : "Chua ket noi"}</p>
    <p class="mb-0"><strong>Handshake:</strong> ${state.ready ? "Da tao shared secret" : "Chua hoan tat"}</p>
  `;
}

function addMessage(sender, plaintext, self = false) {
  const cssClass = self ? "message-self" : "message-other";
  chatMessages.insertAdjacentHTML("beforeend", `<div class="message-item ${cssClass}"><strong>${sender}</strong><div>${plaintext}</div></div>`);
}

connectBtn.addEventListener("click", () => {
  const displayName = displayNameInput.value.trim();
  if (!displayName) {
    logSecurity("Vui long nhap ten hien thi", "warning");
    return;
  }
  state.displayName = displayName;
  socket.emit("join", { display_name: displayName });
});

disconnectBtn.addEventListener("click", () => socket.disconnect());

sendBtn.addEventListener("click", () => {
  const message = messageInput.value.trim();
  if (!message) {
    return;
  }
  socket.emit("send_message", { plaintext: message });
  addMessage("Toi", message, true);
  messageInput.value = "";
});

socket.on("server_dh_public_key", (data) => {
  logSecurity("Da nhan DH public key cua server", "info");
  socket.emit("submit_client_public_key", { public_key_pem: data.public_key_pem });
});

socket.on("handshake_status", (data) => {
  logSecurity(data.message, data.level === "success" ? "success" : "info");
  if (data.level === "success") {
    state.connected = true;
    state.ready = true;
    messageInput.disabled = false;
    sendBtn.disabled = false;
    disconnectBtn.disabled = false;
    connectBtn.disabled = true;
    displayNameInput.disabled = true;
  }
  renderSession();
});

socket.on("online_users", (data) => {
  onlineUsers.innerHTML = data.users.map((user) => `<li class="list-group-item">${user}</li>`).join("");
});

socket.on("new_message", (data) => {
  if (data.sender !== state.displayName) {
    addMessage(data.sender, data.plaintext, false);
  }
});

socket.on("system_message", (data) => logSecurity(data.message, "secondary"));

renderSession();
```

- [ ] **Step 2: Manual browser verification**

Run: open `http://127.0.0.1:5001` in two tabs
Expected: both tabs connect, online list updates, handshake log appears

- [ ] **Step 3: Commit**

```bash
git add lab04/UI-DH-AES/static/js/app.js
git commit -m "feat: add ui dh aes browser client"
```

### Task 8: Strengthen DH Tests and Finalize Message Contract

**Files:**
- Modify: `lab04/UI-DH-AES/tests/test_app.py`
- Modify: `lab04/UI-DH-AES/app.py`

- [ ] **Step 1: Extend app test with relay assertion**

```python
from app import app, socketio, server_public_key
from crypto.dh_aes import export_public_key_pem


def test_relay_payload_contains_ciphertext_metadata():
    first = socketio.test_client(app, flask_test_client=app.test_client())
    second = socketio.test_client(app, flask_test_client=app.test_client())

    first.emit("join", {"display_name": "An"})
    second.emit("join", {"display_name": "Binh"})

    first.get_received()
    second.get_received()

    first.emit("submit_client_public_key", {"public_key_pem": export_public_key_pem(server_public_key)})
    second.emit("submit_client_public_key", {"public_key_pem": export_public_key_pem(server_public_key)})
    first.emit("send_message", {"plaintext": "Xin chao"})

    received = second.get_received()
    assert any(
        item["name"] == "new_message" and "ciphertext" in item["args"][0]
        for item in received
    )
```

- [ ] **Step 2: Add empty-message validation**

```python
if not plaintext:
    emit("handshake_status", {"level": "error", "message": "Tin nhan rong khong hop le"})
    return
```

- [ ] **Step 3: Run all DH-AES tests**

Run: `pytest lab04/UI-DH-AES/tests -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add lab04/UI-DH-AES/app.py lab04/UI-DH-AES/tests/test_app.py
git commit -m "test: finalize ui dh aes message contract"
```

### Task 9: Final Demo Verification

**Files:**
- Verify only

- [ ] **Step 1: Install dependencies**

Run: `pip install -r lab04/UI-DH-AES/requirements.txt`
Expected: packages install successfully

- [ ] **Step 2: Run full test suite**

Run: `pytest lab04/UI-DH-AES/tests -v`
Expected: PASS

- [ ] **Step 3: Run the app**

Run: `python lab04/UI-DH-AES/app.py`
Expected: local server starts without traceback

- [ ] **Step 4: Manual acceptance**

Check:

```text
1. Open two browser tabs
2. Enter two different display names
3. Connect both tabs
4. Confirm handshake log shows DH key exchange and shared secret ready
5. Send messages both directions
6. Disconnect one tab and verify the other remains active
```

- [ ] **Step 5: Commit**

```bash
git add lab04/UI-DH-AES
git commit -m "test: verify ui dh aes demo app"
```
