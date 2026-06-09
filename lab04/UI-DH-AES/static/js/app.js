const socket = io({ autoConnect: false });

const state = {
  displayName: "",
  connected: false,
  handshakeReady: false,
  serverPublicKeyPem: "",
};

const connectBtn = document.getElementById("connectBtn");
const disconnectBtn = document.getElementById("disconnectBtn");
const sendBtn = document.getElementById("sendBtn");
const displayNameInput = document.getElementById("displayName");
const messageInput = document.getElementById("messageInput");
const chatMessages = document.getElementById("chatMessages");
const securityLog = document.getElementById("securityLog");
const onlineUsers = document.getElementById("onlineUsers");
const sessionInfo = document.getElementById("sessionInfo");
const statusBadge = document.getElementById("statusBadge");

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function scrollToBottom(element) {
  element.scrollTop = element.scrollHeight;
}

function renderSession() {
  sessionInfo.innerHTML = `
    <p class="mb-1"><strong>Tên:</strong> ${escapeHtml(state.displayName || "-")}</p>
    <p class="mb-1"><strong>Kết nối:</strong> ${state.connected ? "Đã kết nối" : "Chưa kết nối"}</p>
    <p class="mb-1"><strong>Handshake:</strong> ${state.handshakeReady ? "Đã tạo shared secret" : "Chưa hoàn tất"}</p>
    <p class="mb-0"><strong>Thuật toán:</strong> Diffie-Hellman + AES-CBC</p>
  `;

  if (state.handshakeReady) {
    statusBadge.textContent = "Sẵn sàng chat";
    statusBadge.className = "badge text-bg-success";
  } else if (socket.connected) {
    statusBadge.textContent = "Đang handshake";
    statusBadge.className = "badge text-bg-warning";
  } else {
    statusBadge.textContent = "Chưa kết nối";
    statusBadge.className = "badge text-bg-light";
  }
}

function logSecurity(message, level = "secondary") {
  securityLog.insertAdjacentHTML(
    "beforeend",
    `<div class="alert alert-${level} py-2 mb-2">${escapeHtml(message)}</div>`
  );
  scrollToBottom(securityLog);
}

function addMessage({ sender, plaintext, timestamp }) {
  const isSelf = sender === state.displayName;
  const cssClass = isSelf ? "message-self" : "message-other";
  const senderLabel = isSelf ? "Tôi" : sender;

  chatMessages.insertAdjacentHTML(
    "beforeend",
    `<div class="message-item ${cssClass}">
      <div class="d-flex justify-content-between align-items-center mb-1">
        <strong>${escapeHtml(senderLabel)}</strong>
        <span class="message-meta">${escapeHtml(timestamp || "")}</span>
      </div>
      <div>${escapeHtml(plaintext)}</div>
    </div>`
  );
  scrollToBottom(chatMessages);
}

function setConnectedUi(isConnected) {
  disconnectBtn.disabled = !isConnected;
  messageInput.disabled = !isConnected;
  sendBtn.disabled = !isConnected;
  connectBtn.disabled = isConnected;
  displayNameInput.disabled = isConnected;
}

function resetClientState() {
  state.connected = false;
  state.handshakeReady = false;
  state.serverPublicKeyPem = "";
  setConnectedUi(false);
  renderSession();
}

connectBtn.addEventListener("click", () => {
  const displayName = displayNameInput.value.trim();
  if (!displayName) {
    logSecurity("Vui lòng nhập tên hiển thị trước khi kết nối.", "warning");
    return;
  }

  state.displayName = displayName;
  renderSession();
  socket.connect();
});

disconnectBtn.addEventListener("click", () => {
  socket.disconnect();
});

sendBtn.addEventListener("click", () => {
  const plaintext = messageInput.value.trim();
  if (!plaintext) {
    logSecurity("Tin nhắn rỗng không hợp lệ.", "warning");
    return;
  }

  socket.emit("send_message", { plaintext });
  messageInput.value = "";
  messageInput.focus();
});

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendBtn.click();
  }
});

socket.on("connect", () => {
  socket.emit("join", { display_name: state.displayName });
});

socket.on("server_dh_public_key", (data) => {
  state.serverPublicKeyPem = data.public_key_pem;
  logSecurity("Đã nhận DH public key của server.", "info");
  socket.emit("request_secure_session", { server_public_key_pem: state.serverPublicKeyPem });
});

socket.on("handshake_status", (data) => {
  const levelMap = {
    success: "success",
    error: "danger",
    info: "info",
  };
  logSecurity(data.message, levelMap[data.level] || "secondary");

  if (data.level === "success") {
    state.connected = true;
    state.handshakeReady = true;
    setConnectedUi(true);
  }

  renderSession();
});

socket.on("online_users", (data) => {
  if (!data.users.length) {
    onlineUsers.innerHTML = '<li class="list-group-item text-secondary">Chưa có người dùng</li>';
    return;
  }

  onlineUsers.innerHTML = data.users
    .map((user) => `<li class="list-group-item">${escapeHtml(user)}</li>`)
    .join("");
});

socket.on("new_message", (data) => {
  addMessage(data);
});

socket.on("system_message", (data) => {
  logSecurity(data.message, "secondary");
});

socket.on("disconnect", () => {
  logSecurity("Đã ngắt kết nối khỏi server.", "secondary");
  resetClientState();
});

renderSession();
