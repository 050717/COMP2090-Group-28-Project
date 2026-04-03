/**
 * app.js — Frontend logic
 * All data operations go through the Flask backend at /api/*
 * Session: localStorage only stores { id, username } — no passwords, no records
 */

const API = "";  // Same origin — server.py serves both frontend and API

// ── Session helpers ───────────────────────────────────────────────────────────
function getSession() {
  const raw = localStorage.getItem("session");
  return raw ? JSON.parse(raw) : null;
}

function setSession(user) {
  localStorage.setItem("session", JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem("session");
}

// ── Auth guard ────────────────────────────────────────────────────────────────
function checkLogin() {
  const session = getSession();
  if (!session) {
    alert("Please login first!");
    location.href = "login.html";
    return null;
  }
  const el = document.getElementById("userName");
  if (el) el.textContent = session.username;
  return session;
}

// ── Logout ────────────────────────────────────────────────────────────────────
function logout() {
  clearSession();
  location.href = "login.html";
}

// ── API fetch wrapper ─────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

// ── Login ─────────────────────────────────────────────────────────────────────
async function login() {
  const username = document.getElementById("account").value.trim();
  const password = document.getElementById("password").value.trim();
  if (!username || !password) { alert("Please fill account and password!"); return; }
  try {
    const user = await apiFetch("/api/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    setSession(user);
    location.href = "index.html";
  } catch (e) { alert(e.message); }
}

// ── Register ──────────────────────────────────────────────────────────────────
async function register() {
  const username = document.getElementById("account").value.trim();
  const password = document.getElementById("password").value.trim();
  if (!username || !password) { alert("Please fill all fields!"); return; }
  try {
    await apiFetch("/api/register", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    alert("Register success! Please login.");
  } catch (e) { alert(e.message); }
}

// ── Change password ───────────────────────────────────────────────────────────
async function changePassword() {
  const session = getSession();
  const oldPassword = document.getElementById("oldPwd").value.trim();
  const newPassword = document.getElementById("newPwd").value.trim();
  const confirmPwd  = document.getElementById("confirmPwd").value.trim();
  if (!oldPassword || !newPassword || !confirmPwd) { alert("Please fill all fields!"); return; }
  if (newPassword !== confirmPwd) { alert("Passwords do not match!"); return; }
  try {
    await apiFetch("/api/change-password", {
      method: "POST",
      body: JSON.stringify({ username: session.username, oldPassword, newPassword }),
    });
    alert("Password changed! Please login again.");
    logout();
  } catch (e) { alert(e.message); }
}

// ── Calculate & render balance summary ───────────────────────────────────────
async function calculateMoney() {
  const session = getSession();
  if (!session) return;
  try {
    const records = await apiFetch(`/api/transactions?user_id=${session.id}`);
    let totalIn = 0, totalOut = 0;
    records.forEach(r => {
      const n = parseFloat(r.amount);
      if (r.type === "income") totalIn += n;
      else totalOut += n;
    });
    const incomeEl  = document.getElementById("income");
    const expenseEl = document.getElementById("expense");
    const balanceEl = document.getElementById("balance");
    if (incomeEl)  incomeEl.textContent  = "$" + totalIn.toFixed(2);
    if (expenseEl) expenseEl.textContent = "$" + totalOut.toFixed(2);
    if (balanceEl) balanceEl.textContent = "$" + (totalIn - totalOut).toFixed(2);
  } catch (e) { console.error("calculateMoney:", e); }
}

// ── Transaction (deposit / withdraw / transfer) ───────────────────────────────
async function doTransaction() {
  const session = getSession();
  const type   = document.getElementById("type").value;
  const amount = parseFloat(document.getElementById("amount").value);
  const txDate = document.getElementById("date").value;
  const remark = (document.getElementById("remark")?.value || "").trim();
  const target = (document.getElementById("targetAccount")?.value || "").trim();

  if (!amount || !txDate) { alert("Please fill required fields!"); return; }
  if (amount <= 0) { alert("Amount must be > 0"); return; }
  if (!confirm(`Confirm ${type} $${amount.toFixed(2)}?`)) return;

  try {
    if (type === "Transfer") {
      if (!target) { alert("Enter target account!"); return; }
      await apiFetch("/api/transfer", {
        method: "POST",
        body: JSON.stringify({
          from_user_id: session.id,
          to_username: target,
          amount,
          date: txDate,
          description: remark,
        }),
      });
    } else {
      const backendType = type === "Deposit" ? "income" : "expense";
      await apiFetch("/api/transactions", {
        method: "POST",
        body: JSON.stringify({
          user_id: session.id,
          type: backendType,
          amount,
          category: type,
          description: remark,
          date: txDate,
        }),
      });
    }
    alert(type + " success!");
    location.href = "record-list.html";
  } catch (e) { alert(e.message); }
}

// ── Load transaction history ──────────────────────────────────────────────────
async function loadRecords() {
  const session = getSession();
  if (!session) return;
  const container = document.getElementById("listContainer");
  container.innerHTML = `<div class="record-item" style="justify-content:center;color:#999;">Loading...</div>`;

  try {
    const records = await apiFetch(`/api/transactions?user_id=${session.id}`);

    // Render balance summary if elements exist
    let totalIn = 0, totalOut = 0;
    records.forEach(r => {
      const n = parseFloat(r.amount);
      if (r.type === "income") totalIn += n;
      else totalOut += n;
    });
    const incomeEl  = document.getElementById("income");
    const expenseEl = document.getElementById("expense");
    const balanceEl = document.getElementById("balance");
    if (incomeEl)  incomeEl.textContent  = "$" + totalIn.toFixed(2);
    if (expenseEl) expenseEl.textContent = "$" + totalOut.toFixed(2);
    if (balanceEl) balanceEl.textContent = "$" + (totalIn - totalOut).toFixed(2);

    container.innerHTML = "";

    if (records.length === 0) {
      container.innerHTML = `<div class="record-item" style="justify-content:center;color:#999;">No records yet</div>`;
      return;
    }

    records.forEach(r => {
      let displayType, cssClass, sign;
      if (r.type === "income") {
        displayType = r.category === "Transfer" ? "Transfer In" : "Deposit";
        cssClass = "deposit"; sign = "+";
      } else {
        displayType = r.category === "Transfer" ? "Transfer Out" : "Withdraw";
        cssClass = r.category === "Transfer" ? "transfer" : "withdraw";
        sign = "-";
      }
      const div = document.createElement("div");
      div.className = "record-item";
      div.innerHTML = `
        <div>
          <span class="${cssClass}">${displayType}</span>
          <div style="font-size:0.85rem;color:#666;margin-top:2px;">${r.date}</div>
          ${r.description ? `<small style="color:#999;">${r.description}</small>` : ""}
        </div>
        <div style="display:flex;align-items:center;gap:0.8rem;">
          <span class="${cssClass}" style="font-size:1.1rem;font-weight:bold;">${sign}$${parseFloat(r.amount).toFixed(2)}</span>
          <button class="delete-btn" onclick="deleteRecord(${r.id})">✕</button>
        </div>
      `;
      container.appendChild(div);
    });
  } catch (e) {
    container.innerHTML = `<div class="record-item" style="color:red;">Failed to load: ${e.message}</div>`;
  }
}

// ── Delete a record ───────────────────────────────────────────────────────────
async function deleteRecord(id) {
  if (!confirm("Delete this record?")) return;
  try {
    await apiFetch(`/api/transactions/${id}`, { method: "DELETE" });
    loadRecords();
  } catch (e) { alert(e.message); }
}
