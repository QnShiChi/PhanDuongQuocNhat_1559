# UI-AES-RSA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained web app in `lab04/UI-AES-RSA` that demonstrates multi-client secure chat through a server using an RSA handshake to establish per-client AES session keys.

**Architecture:** Use one Flask application to serve the HTML UI and host Socket.IO events for realtime chat. Keep crypto logic in focused helper modules so the app layer only manages session state, handshake flow, message relay, and UI events.

**Tech Stack:** Python, Flask, Flask-SocketIO, PyCryptodome, HTML, Bootstrap 5, vanilla JavaScript, pytest

---

## File Structure

- Create: `lab04/UI-AES-RSA/app.py` - Flask app, Socket.IO event handlers, in-memory session registry
- Create: `lab04/UI-AES-RSA/requirements.txt` - runtime dependencies
- Create: `lab04/UI-AES-RSA/crypto/__init__.py` - crypto package marker
- Create: `lab04/UI-AES-RSA/crypto/rsa_aes.py` - RSA keypair generation, AES session key helpers, encrypt/decrypt helpers
- Create: `lab04/UI-AES-RSA/templates/index.html` - single-page Bootstrap UI
- Create: `lab04/UI-AES-RSA/static/css/styles.css` - layout polish
- Create: `lab04/UI-AES-RSA/static/js/app.js` - Socket.IO client, connect/send/disconnect workflow, UI rendering
- Create: `lab04/UI-AES-RSA/tests/test_crypto.py` - unit tests for RSA/AES helper behavior
- Create: `lab04/UI-AES-RSA/tests/test_app.py` - server handshake and relay tests with Socket.IO test client

### Task 1: Scaffold Project Files

**Files:**
- Create: `lab04/UI-AES-RSA/requirements.txt`
- Create: `lab04/UI-AES-RSA/crypto/__init__.py`

- [ ] **Step 1: Create dependency manifest**

```text
Flask==3.0.3
Flask-SocketIO==5.3.6
python-socketio==5.11.4
eventlet==0.36.1
pycryptodome==3.20.0
pytest==8.2.2
```

- [ ] **Step 2: Create crypto package marker**

```python
# lab04/UI-AES-RSA/crypto/__init__.py
```

- [ ] **Step 3: Verify files exist**

Run: `Get-ChildItem lab04\UI-AES-RSA -Recurse`
Expected: shows `requirements.txt` and `crypto\__init__.py`

- [ ] **Step 4: Commit**

```bash
git add lab04/UI-AES-RSA/requirements.txt lab04/UI-AES-RSA/crypto/__init__.py
git commit -m "chore: scaffold ui aes rsa project"
```

### Task 2: Write Crypto Tests First

**Files:**
- Test: `lab04/UI-AES-RSA/tests/test_crypto.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest lab04/UI-AES-RSA/tests/test_crypto.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing symbol errors for `crypto.rsa_aes`

- [ ] **Step 3: Commit the failing test**

```bash
git add lab04/UI-AES-RSA/tests/test_crypto.py
git commit -m "test: define rsa aes crypto expectations"
```

### Task 3: Implement RSA/AES Helper Module

**Files:**
- Create: `lab04/UI-AES-RSA/crypto/rsa_aes.py`
- Modify: `lab04/UI-AES-RSA/tests/test_crypto.py`

- [ ] **Step 1: Write minimal implementation**

```python
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
    return base64.b64encode(cipher.encrypt(aes_key)).decode("utf-8")


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
```

- [ ] **Step 2: Run test to verify it passes**

Run: `pytest lab04/UI-AES-RSA/tests/test_crypto.py -v`
Expected: PASS for both crypto tests

- [ ] **Step 3: Commit**

```bash
git add lab04/UI-AES-RSA/crypto/rsa_aes.py lab04/UI-AES-RSA/tests/test_crypto.py
git commit -m "feat: add rsa aes crypto helpers"
```

### Task 4: Write Failing Server Tests

**Files:**
- Test: `lab04/UI-AES-RSA/tests/test_app.py`

- [ ] **Step 1: Write the failing test**

```python
from app import app, socketio


def test_join_returns_public_key_and_handshake_success():
    client = socketio.test_client(app, flask_test_client=app.test_client())

    client.emit("join", {"display_name": "An"})
    received = client.get_received()

    event_names = [item["name"] for item in received]
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
    first.emit("send_message", {"plaintext": "Chao ban"})

    received = second.get_received()
    assert any(item["name"] == "new_message" for item in received)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest lab04/UI-AES-RSA/tests/test_app.py -v`
Expected: FAIL because `app.py` and socket handlers do not exist yet

- [ ] **Step 3: Commit the failing test**

```bash
git add lab04/UI-AES-RSA/tests/test_app.py
git commit -m "test: define ui aes rsa server behavior"
```

### Task 5: Implement Flask + Socket.IO Server

**Files:**
- Create: `lab04/UI-AES-RSA/app.py`

- [ ] **Step 1: Write minimal implementation**

```python
from datetime import datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from crypto.rsa_aes import (
    create_rsa_keypair,
    create_aes_key,
    decrypt_aes_key_with_rsa,
    decrypt_message,
    encrypt_aes_key_with_rsa,
    encrypt_message,
    export_public_key_pem,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "ui-aes-rsa-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

server_private_key, server_public_key = create_rsa_keypair()
client_sessions = {}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def handle_join(data):
    sid = request.sid
    display_name = data["display_name"].strip()
    client_sessions[sid] = {
        "display_name": display_name,
        "aes_key": None,
        "ready": False,
    }
    emit("server_public_key", {"public_key_pem": export_public_key_pem(server_public_key)})
    emit("handshake_status", {"level": "info", "message": "Da nhan RSA public key"})
    emit_online_users()


@socketio.on("request_secure_session")
def handle_request_secure_session(data):
    sid = request.sid
    aes_key = create_aes_key()
    encrypted_key = encrypt_aes_key_with_rsa(server_public_key, aes_key)
    client_sessions[sid]["aes_key"] = decrypt_aes_key_with_rsa(server_private_key, encrypted_key)
    client_sessions[sid]["ready"] = True
    emit("handshake_status", {"level": "success", "message": "Handshake AES-RSA thanh cong"})
    emit("system_message", {"message": f"{client_sessions[sid]['display_name']} da vao phong"}, broadcast=True)


@socketio.on("send_message")
def handle_send_message(data):
    sid = request.sid
    session = client_sessions[sid]
    plaintext = decrypt_message(session["aes_key"], data)
    timestamp = datetime.now().strftime("%H:%M:%S")
    for target_sid, target_session in client_sessions.items():
        if not target_session["ready"]:
            continue
        payload = encrypt_message(target_session["aes_key"], plaintext)
        emit(
            "new_message",
            {
                "sender": session["display_name"],
                "plaintext": plaintext,
                "timestamp": timestamp,
                "encrypted_payload": payload,
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
    emit(
        "online_users",
        {"users": [item["display_name"] for item in client_sessions.values()]},
        broadcast=True,
    )


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
```

- [ ] **Step 2: Run server tests**

Run: `pytest lab04/UI-AES-RSA/tests/test_app.py -v`
Expected: PASS for join and relay behavior, or one focused failure that points to event payload mismatch

- [ ] **Step 3: Adjust payload names if needed and rerun**

Run: `pytest lab04/UI-AES-RSA/tests/test_app.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add lab04/UI-AES-RSA/app.py
git commit -m "feat: add ui aes rsa socket server"
```

### Task 6: Build Bootstrap UI

**Files:**
- Create: `lab04/UI-AES-RSA/templates/index.html`
- Create: `lab04/UI-AES-RSA/static/css/styles.css`

- [ ] **Step 1: Create page template**

```html
<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Secure Chat AES-RSA</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
  </head>
  <body class="bg-body-tertiary">
    <div class="container py-4">
      <div class="row g-3">
        <div class="col-lg-4">
          <div class="card shadow-sm mb-3">
            <div class="card-body">
              <h1 class="h4">Secure Chat AES-RSA</h1>
              <p class="text-muted mb-3">Chat nhieu client qua server voi AES-RSA handshake.</p>
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
  background: #d1e7dd;
}

.message-other {
  background: #f8f9fa;
}
```

- [ ] **Step 3: Verify template route loads**

Run: `python lab04/UI-AES-RSA/app.py`
Expected: server starts on `http://127.0.0.1:5000`

- [ ] **Step 4: Commit**

```bash
git add lab04/UI-AES-RSA/templates/index.html lab04/UI-AES-RSA/static/css/styles.css
git commit -m "feat: add ui aes rsa bootstrap layout"
```

### Task 7: Implement Browser Client Logic

**Files:**
- Create: `lab04/UI-AES-RSA/static/js/app.js`

- [ ] **Step 1: Add client workflow**

```javascript
const socket = io();
const state = { connected: false, displayName: "", handshakeReady: false };

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
    <p class="mb-0"><strong>Handshake:</strong> ${state.handshakeReady ? "San sang" : "Chua hoan tat"}</p>
  `;
}

function addMessage(sender, plaintext, self = false) {
  const cssClass = self ? "message-self" : "message-other";
  chatMessages.insertAdjacentHTML("beforeend", `<div class="message-item ${cssClass}"><strong>${sender}</strong><div>${plaintext}</div></div>`);
}

connectBtn.addEventListener("click", () => {
  const displayName = displayNameInput.value.trim();
  if (!displayName) {
    logSecurity("Vui lòng nhập tên hiển thị", "warning");
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

socket.on("server_public_key", (data) => {
  logSecurity("Đã nhận RSA public key từ server", "info");
  socket.emit("request_secure_session", { public_key_pem: data.public_key_pem });
});

socket.on("handshake_status", (data) => {
  logSecurity(data.message, data.level === "success" ? "success" : "info");
  if (data.level === "success") {
    state.connected = true;
    state.handshakeReady = true;
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

- [ ] **Step 2: Update server handshake event names to match the browser flow**

Use this server-side event instead of `submit_aes_key`:

```python
@socketio.on("request_secure_session")
def handle_request_secure_session(data):
    sid = request.sid
    aes_key = create_aes_key()
    encrypted_key = encrypt_aes_key_with_rsa(server_public_key, aes_key)
    client_sessions[sid]["aes_key"] = decrypt_aes_key_with_rsa(server_private_key, encrypted_key)
    client_sessions[sid]["ready"] = True
    emit("handshake_status", {"level": "success", "message": "Handshake AES-RSA thành công"})
    emit("system_message", {"message": f"{client_sessions[sid]['display_name']} đã vào phòng"}, broadcast=True)
```

- [ ] **Step 3: Manual browser verification**

Run: open `http://127.0.0.1:5000` in two tabs
Expected: both tabs can connect, online list updates, handshake log appears

- [ ] **Step 4: Commit**

```bash
git add lab04/UI-AES-RSA/static/js/app.js lab04/UI-AES-RSA/templates/index.html
git commit -m "feat: add ui aes rsa browser client"
```

### Task 8: Finalize Message Contract and Validation

**Files:**
- Modify: `lab04/UI-AES-RSA/static/js/app.js`
- Modify: `lab04/UI-AES-RSA/app.py`

- [ ] **Step 1: Use server-side AES encryption for relay metadata**

Client send event:

```javascript
socket.emit("send_message", { plaintext: message });
```

Server relay handler:

```python
@socketio.on("send_message")
def handle_send_message(data):
    sid = request.sid
    session = client_sessions[sid]
    plaintext = data["plaintext"].strip()
    if not plaintext:
        emit("handshake_status", {"level": "error", "message": "Tin nhan rong khong hop le"})
        return
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
                "timestamp": timestamp,
                "ciphertext": encrypted_payload["ciphertext"],
                "iv": encrypted_payload["iv"],
            },
            to=target_sid,
        )
```

- [ ] **Step 2: Update tests to match final message contract**

```python
assert any(
    item["name"] == "new_message" and "ciphertext" in item["args"][0]
    for item in received
)
```

- [ ] **Step 3: Add empty-message validation**

```python
if not plaintext:
    emit("handshake_status", {"level": "error", "message": "Tin nhắn rỗng không hợp lệ"})
    return
```

- [ ] **Step 4: Run all AES-RSA tests**

Run: `pytest lab04/UI-AES-RSA/tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add lab04/UI-AES-RSA/app.py lab04/UI-AES-RSA/static/js/app.js lab04/UI-AES-RSA/tests/test_app.py
git commit -m "refactor: finalize ui aes rsa message flow"
```

### Task 9: Final Demo Verification

**Files:**
- Verify only

- [ ] **Step 1: Install dependencies**

Run: `pip install -r lab04/UI-AES-RSA/requirements.txt`
Expected: packages install successfully

- [ ] **Step 2: Run full test suite**

Run: `pytest lab04/UI-AES-RSA/tests -v`
Expected: PASS

- [ ] **Step 3: Run the app**

Run: `python lab04/UI-AES-RSA/app.py`
Expected: local server starts without traceback

- [ ] **Step 4: Manual acceptance**

Check:

```text
1. Open two browser tabs
2. Enter two different display names
3. Connect both tabs
4. Confirm handshake log shows RSA public key + AES session ready
5. Send messages both directions
6. Disconnect one tab and verify the other remains active
```

- [ ] **Step 5: Commit**

```bash
git add lab04/UI-AES-RSA
git commit -m "test: verify ui aes rsa demo app"
```
