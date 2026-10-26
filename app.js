/* Frontend logic: talks to the Flask JSON API with fetch(). */
const $ = (id) => document.getElementById(id);
const messages = $("messages");
const input = $("input");
const form = $("form");
const sendBtn = $("send");

/* ---------- Helpers ---------- */
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Tiny, safe formatter: ```code``` blocks, `inline`, **bold**.
function format(text) {
  let html = escapeHtml(text);
  html = html.replace(/```(?:\w+)?\n?([\s\S]*?)```/g, "<pre><code>$1</code></pre>");
  html = html.replace(/`([^`\n]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*\n]+)\*\*/g, "<b>$1</b>");
  return html;
}

function scrollDown() { messages.scrollTop = messages.scrollHeight; }

function hideWelcome() {
  const w = $("welcome");
  if (w) w.remove();
}

function addMessage(role, text, seconds) {
  hideWelcome();
  const row = document.createElement("div");
  row.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = role === "user" ? escapeHtml(text) : format(text);
  if (seconds !== undefined && seconds !== null) {
    const meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = `answered in ${seconds}s`;
    bubble.appendChild(meta);
  }
  row.appendChild(bubble);
  messages.appendChild(row);
  scrollDown();
  return row;
}

function addTyping() {
  const row = document.createElement("div");
  row.className = "msg bot";
  row.innerHTML = '<div class="bubble typing"><span></span><span></span><span></span></div>';
  messages.appendChild(row);
  scrollDown();
  return row;
}

async function api(url, options) {
  const res = await fetch(url, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

/* ---------- Sending messages ---------- */
async function send(text) {
  text = text.trim();
  if (!text) return;
  addMessage("user", text);
  input.value = "";
  autoGrow();
  sendBtn.disabled = true;
  const typing = addTyping();
  try {
    const data = await api("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    typing.remove();
    addMessage("bot", data.answer, data.seconds);
  } catch (err) {
    typing.remove();
    addMessage("bot error", err.message);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => { e.preventDefault(); send(input.value); });

// Enter sends, Shift+Enter makes a new line
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); }
});

function autoGrow() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 160) + "px";
}
input.addEventListener("input", autoGrow);

document.querySelectorAll(".chip").forEach((chip) =>
  chip.addEventListener("click", () => send(chip.textContent))
);

/* ---------- Restore saved history on load ---------- */
(async function loadHistory() {
  try {
    const rows = await api("/api/history");
    rows.forEach((r) => {
      addMessage("user", String(r.question));
      addMessage("bot", String(r.answer), r.response_time_sec);
    });
  } catch (_) { /* no history yet: keep the welcome screen */ }
})();

/* ---------- New conversation ---------- */
$("btn-new").addEventListener("click", async () => {
  try {
    await api("/api/reset", { method: "POST" });
    messages.innerHTML = "";
    addMessage("bot", "Conversation reset. Ask me something new!");
  } catch (err) {
    addMessage("bot error", err.message);
  }
  closeSidebar();
});

/* ---------- Modal (stats / charts / models) ---------- */
const modal = $("modal");
function openModal(title, html) {
  $("modal-title").textContent = title;
  $("modal-body").innerHTML = html;
  modal.hidden = false;
  closeSidebar();
}
function closeModal() { modal.hidden = true; }
$("modal-close").addEventListener("click", closeModal);
modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });

$("btn-stats").addEventListener("click", async () => {
  openModal("Statistics", "<p>Loading…</p>");
  try {
    const s = await api("/api/stats");
    if (s.empty) { $("modal-body").innerHTML = "<p>No chats yet. Ask a question first!</p>"; return; }
    const stat = (v, l) => `<div class="stat"><b>${v}</b><span>${l}</span></div>`;
    $("modal-body").innerHTML =
      '<div class="stat-grid">' +
      stat(s.total, "Total chats") +
      stat(s.avg_time + "s", "Average response time") +
      stat(s.median_time + "s", "Median response time") +
      stat(s.max_time + "s", "Slowest response") +
      stat(s.avg_words, "Average answer (words)") +
      (s.prediction !== null ? stat(s.prediction, "Predicted words for a 10-word question") : "") +
      "</div>";
  } catch (err) { $("modal-body").textContent = err.message; }
});

$("btn-charts").addEventListener("click", async () => {
  openModal("Charts", "<p>Generating charts…</p>");
  try {
    const data = await api("/api/charts", { method: "POST" });
    const stamp = Date.now(); // cache-buster so fresh charts always load
    $("modal-body").innerHTML = data.charts
      .map((c) => `<h4>${escapeHtml(c.title)}</h4><img src="${c.url}?t=${stamp}" alt="${escapeHtml(c.title)}">`)
      .join("");
  } catch (err) { $("modal-body").textContent = err.message; }
});

$("btn-models").addEventListener("click", async () => {
  openModal("Available models", "<p>Loading…</p>");
  try {
    const data = await api("/api/models");
    $("modal-body").innerHTML = "<ul>" + data.models.map((m) => `<li>${escapeHtml(m)}</li>`).join("") + "</ul>";
  } catch (err) { $("modal-body").textContent = err.message; }
});

/* ---------- Theme + mobile sidebar ---------- */
function applyTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  try { localStorage.setItem("theme", t); } catch (_) {}
}
let saved = null;
try { saved = localStorage.getItem("theme"); } catch (_) {}
applyTheme(saved || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
$("btn-theme").addEventListener("click", () =>
  applyTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark")
);

function closeSidebar() { $("sidebar").classList.remove("open"); }
$("btn-menu").addEventListener("click", () => $("sidebar").classList.toggle("open"));
