/* global app.js — 智校通前端逻辑 */

const API = "";   // 同域部署，前缀留空
let affairsChatHistory = [];

/* ===== 工具函数 ===== */
function showLoading() { document.getElementById("loadingOverlay").classList.add("active"); }
function hideLoading() { document.getElementById("loadingOverlay").classList.remove("active"); }

function showToast(msg, duration = 2500) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), duration);
}

function showResult(id, html) {
  const box = document.getElementById(id);
  box.classList.add("visible");
  box.innerHTML = `
    <div class="result-inner">${html}</div>
    <div class="result-actions">
      <button class="btn-copy" onclick="copyResult('${id}')">📋 复制</button>
      <button class="btn-download" onclick="downloadResult('${id}')">📥 下载</button>
      <button class="btn-clear" onclick="clearResult('${id}')">🗑️ 清除</button>
    </div>`;
  // 渲染数学公式
  if (typeof renderMathInElement !== 'undefined') {
    renderMathInElement(box, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false},
        {left: '\\(', right: '\\)', display: false},
        {left: '\\[', right: '\\]', display: true}
      ],
      throwOnError: false
    });
  }
}

function clearResult(id) {
  const box = document.getElementById(id);
  box.classList.remove("visible");
  box.innerHTML = "";
}

function copyResult(id) {
  const inner = document.querySelector(`#${id} .result-inner`);
  if (!inner) return;
  const text = inner.innerText;

  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => showToast("✅ 已复制到剪贴板")).catch(() => showToast("❌ 复制失败"));
    return;
  }

  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.left = "-9999px";
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  try {
    document.execCommand("copy");
    showToast("✅ 已复制到剪贴板");
  } catch (e) {
    showToast("❌ 复制失败");
  } finally {
    document.body.removeChild(ta);
  }
}

function downloadResult(id) {
  const inner = document.querySelector(`#${id} .result-inner`);
  if (!inner) return;
  const text = inner.innerText;
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const ts = new Date().toISOString().slice(0, 16).replace("T", "_").replace(":", "-");
  a.download = `智校通_${id}_${ts}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast("✅ 已下载文件");
}

/** 简单 Markdown → HTML（无依赖） */
function md2html(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/^\s*#{3}\s+(.+)$/gm, "<h3>$1</h3>")
    .replace(/^\s*#{2}\s+(.+)$/gm, "<h2>$1</h2>")
    .replace(/^\s*#{1}\s+(.+)$/gm, "<h1>$1</h1>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/^\s*>\s+(.+)$/gm, "<blockquote>$1</blockquote>")
    .replace(/^\s*[-*]\s+(.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    .replace(/^\s*\d+\.\s+(.+)$/gm, "<li-ol>$1</li-ol>")
    .replace(/(<li-ol>.*<\/li-ol>\n?)+/g, m => `<ol>${m.replace(/<\/?li-ol>/g, t => t === "<li-ol>" ? "<li>" : "</li>")}</ol>`)
    .replace(/\n{2,}/g, "</p><p>")
    .replace(/^(?!<[a-z])(.+)$/gm, m => m.trim() ? `<p>${m}</p>` : "");
}

async function apiPost(url, body, isFormData = false) {
  const opts = { method: "POST" };
  if (isFormData) {
    opts.body = body;
  } else {
    opts.headers = { "Content-Type": "application/json" };
    opts.body = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(API + url, opts);
  } catch (e) {
    throw new Error("网络连接失败，请检查后端服务是否已启动");
  }

  const contentType = res.headers.get("content-type") || "";
  let data = {};

  if (contentType.includes("application/json")) {
    try {
      data = await res.json();
    } catch (e) {
      data = {};
    }
  } else {
    const text = await res.text();
    data = { error: text || `服务返回异常响应（${res.status}）` };
  }

  if (!res.ok) throw new Error(data.error || `请求失败（${res.status}）`);
  return data;
}

/* ===== 导航 Tab ===== */
document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
  });
});

/* ===== 文件上传 ===== */
const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("fileInput");
if (uploadArea) {
  uploadArea.addEventListener("click", () => fileInput.click());
  uploadArea.addEventListener("dragover", e => { e.preventDefault(); uploadArea.style.borderColor = "var(--primary)"; });
  uploadArea.addEventListener("dragleave", () => { uploadArea.style.borderColor = ""; });
  uploadArea.addEventListener("drop", e => {
    e.preventDefault();
    uploadArea.style.borderColor = "";
    const f = e.dataTransfer.files[0];
    if (f) { fileInput.files = e.dataTransfer.files; updateFileLabel(f.name); }
  });
  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) updateFileLabel(fileInput.files[0].name);
  });
}
function updateFileLabel(name) {
  document.getElementById("uploadPlaceholder").style.display = "none";
  const sel = document.getElementById("uploadSelected");
  sel.style.display = "block";
  sel.textContent = "📎 " + name;
}

/* ===== 学术辅助 ===== */
async function extractKnowledge() {
  const file = fileInput && fileInput.files[0];
  const text = document.getElementById("extractText").value.trim();
  if (!file && !text) { showToast("⚠️ 请上传文件或输入课程内容"); return; }
  showLoading();
  try {
    let data;
    if (file) {
      const fd = new FormData();
      fd.append("file", file);
      if (text) fd.append("text", text);
      data = await apiPost("/api/academic/extract-knowledge", fd, true);
    } else {
      data = await apiPost("/api/academic/extract-knowledge", { text });
    }
    showResult("extractResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

async function generateQuestions() {
  const content = document.getElementById("qContent").value.trim();
  const count = parseInt(document.getElementById("qCount").value) || 5;
  const type = document.getElementById("qType").value;
  if (!content) { showToast("⚠️ 请输入知识点内容"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/academic/generate-questions", { content, count, type });
    showResult("questionsResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

async function generateStudyPlan() {
  const subject = document.getElementById("spSubject").value.trim();
  const exam_date = document.getElementById("spExamDate").value;
  const weak_points = document.getElementById("spWeak").value.trim();
  const available_hours = document.getElementById("spHours").value;
  if (!subject) { showToast("⚠️ 请填写课程名称"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/academic/study-plan", { subject, exam_date, weak_points, available_hours });
    showResult("studyPlanResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

async function generateLiteratureReview() {
  const topic = document.getElementById("litTopic").value.trim();
  const field = document.getElementById("litField").value.trim();
  if (!topic) { showToast("⚠️ 请填写研究主题"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/academic/literature-review", { topic, field });
    showResult("litResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

async function generateLabReport() {
  const experiment = document.getElementById("labName").value.trim();
  const purpose = document.getElementById("labPurpose").value.trim();
  const method = document.getElementById("labMethod").value.trim();
  const data_input = document.getElementById("labData").value.trim();
  if (!experiment) { showToast("⚠️ 请填写实验名称"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/academic/lab-report", { experiment, purpose, method, data: data_input });
    showResult("labResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

async function analyzeWrongQuestions() {
  const questions = document.getElementById("wqContent").value.trim();
  const subject = document.getElementById("wqSubject").value.trim();
  if (!questions) { showToast("⚠️ 请输入错题内容"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/academic/wrong-questions", { questions, subject });
    showResult("wqResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

/* ===== 校园事务 ===== */
function appendChatMessage(chatId, role, html) {
  const chat = document.getElementById(chatId);
  const div = document.createElement("div");
  div.className = "message " + (role === "user" ? "user-msg" : "bot-msg");
  div.innerHTML = `
    <span class="msg-avatar">${role === "user" ? "🧑" : "🤖"}</span>
    <div class="msg-content">${html}</div>`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function quickQuery(query) {
  document.getElementById("affairsInput").value = query;
  sendAffairsMessage();
}

async function sendAffairsMessage() {
  const input = document.getElementById("affairsInput");
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  appendChatMessage("affairsChat", "user", escapeHtml(message));
  affairsChatHistory.push({ role: "user", content: message });
  showLoading();
  try {
    const data = await apiPost("/api/affairs/chat", { message, history: affairsChatHistory.slice(-10) });
    const html = md2html(data.result);
    appendChatMessage("affairsChat", "bot", html);
    affairsChatHistory.push({ role: "assistant", content: data.result });
  } catch (e) {
    appendChatMessage("affairsChat", "bot", `<span style="color:var(--danger)">❌ ${escapeHtml(e.message)}</span>`);
  } finally { hideLoading(); }
}

function chatKeydown(e, type) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (type === "affairs") sendAffairsMessage();
  }
}

async function generateTemplate() {
  const type = document.getElementById("templateType").value;
  if (!type) { showToast("⚠️ 请选择申请类型"); return; }
  const user_info = {
    姓名: document.getElementById("tmplName").value.trim(),
    学号: document.getElementById("tmplId").value.trim(),
    专业班级: document.getElementById("tmplClass").value.trim(),
    联系方式: document.getElementById("tmplContact").value.trim(),
  };
  showLoading();
  try {
    const data = await apiPost("/api/affairs/template", { type, user_info });
    showResult("templateResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

/* ===== 成长助手 ===== */
async function getCareerPlan() {
  const major = document.getElementById("cpMajor").value.trim();
  const grade = document.getElementById("cpGrade").value;
  const interests = document.getElementById("cpInterests").value.trim();
  const goals = document.getElementById("cpGoals").value.trim();
  if (!major) { showToast("⚠️ 请填写专业"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/growth/career-plan", { major, grade, interests, goals });
    showResult("careerPlanResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

async function optimizeResume() {
  const resume = document.getElementById("resumeContent").value.trim();
  const position = document.getElementById("resumePos").value.trim();
  const industry = document.getElementById("resumeIndustry").value.trim();
  if (!resume) { showToast("⚠️ 请粘贴简历内容"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/growth/resume", { resume, position, industry });
    showResult("resumeResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

function switchInterviewMode(mode, btn) {
  document.querySelectorAll(".tab-sub-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  document.getElementById("interviewPractice").style.display = mode === "practice" ? "block" : "none";
  document.getElementById("interviewGenerate").style.display = mode === "generate" ? "block" : "none";
}

async function practiceInterview() {
  const position = document.getElementById("ivPosition").value.trim();
  const question = document.getElementById("ivQuestion").value.trim();
  const answer = document.getElementById("ivAnswer").value.trim();
  if (!question || !answer) { showToast("⚠️ 请填写面试题目和您的回答"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/growth/interview", { position, question, answer, mode: "feedback" });
    showResult("interviewResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

async function generateInterviewQuestions() {
  const position = document.getElementById("ivGenPosition").value.trim();
  if (!position) { showToast("⚠️ 请填写目标岗位"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/growth/interview", { position, mode: "generate" });
    showResult("interviewResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

function campusNav(query) {
  document.getElementById("campusNavInput").value = query;
  askCampusNav();
}

async function askCampusNav() {
  const query = document.getElementById("campusNavInput").value.trim();
  if (!query) { showToast("⚠️ 请输入问题"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/growth/campus-nav", { query });
    showResult("campusNavResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

/* ===== 考试提醒 ===== */
function addExamItem() {
  const list = document.getElementById("examList");
  const item = document.createElement("div");
  item.className = "exam-item";
  item.innerHTML = `
    <div class="exam-item-header">
      <button class="btn-remove-exam" onclick="removeExamItem(this)" title="删除">✕</button>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>考试名称 *</label>
        <input type="text" class="er-name" placeholder="如：线性代数期末" />
      </div>
      <div class="form-group">
        <label>考试日期</label>
        <input type="date" class="er-date" />
      </div>
    </div>
    <div class="form-group">
      <label>备注</label>
      <input type="text" class="er-notes" placeholder="如：占总分50%，重点复习第3-5章" />
    </div>`;
  list.appendChild(item);
}

function removeExamItem(btn) {
  const item = btn.closest(".exam-item");
  const list = document.getElementById("examList");
  if (list.querySelectorAll(".exam-item").length > 1) {
    item.remove();
  } else {
    showToast("⚠️ 至少保留一门考试");
  }
}

async function generateExamReminder() {
  const semester_start = document.getElementById("erSemesterStart").value;
  const items = document.querySelectorAll(".exam-item");
  const exams = [];
  items.forEach(item => {
    const name = item.querySelector(".er-name").value.trim();
    const date = item.querySelector(".er-date").value;
    const notes = item.querySelector(".er-notes").value.trim();
    if (name) exams.push({ name, date, notes });
  });
  if (exams.length === 0) { showToast("⚠️ 请至少填写一门考试名称"); return; }
  showLoading();
  try {
    const data = await apiPost("/api/growth/exam-reminder", { exams, semester_start });
    showResult("examReminderResult", md2html(data.result));
  } catch (e) { showToast("❌ " + e.message); } finally { hideLoading(); }
}

/* ===== 工具 ===== */
function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
