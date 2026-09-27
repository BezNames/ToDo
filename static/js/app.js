/* Логика фронтенда ToDo: авторизация, задачи, приоритеты, сроки, статистика */
const $ = (sel) => document.querySelector(sel);

const state = {
  user: null,
  tasks: [],
  filter: 'all',        // all | active | done | overdue
  search: '',
  sort: 'created',      // created | priority | due
  editingId: null,
};

const PRIORITY_META = {
  high:   { label: '🔴 Высокий', cls: 'p-high' },
  medium: { label: '⚪ Обычный', cls: 'p-medium' },
  low:    { label: '🟢 Низкий',  cls: 'p-low' },
};

/* ---------- Утилиты ---------- */
function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleString('ru-RU', { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' });
}

function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function isOverdue(t) {
  return !t.completed && t.due_date && t.due_date < todayStr();
}

function formatDue(due) {
  if (!due) return '';
  const today = todayStr();
  if (due === today) return 'сегодня';
  const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1);
  const tom = `${tomorrow.getFullYear()}-${String(tomorrow.getMonth() + 1).padStart(2, '0')}-${String(tomorrow.getDate()).padStart(2, '0')}`;
  if (due === tom) return 'завтра';
  const yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1);
  const yes = `${yesterday.getFullYear()}-${String(yesterday.getMonth() + 1).padStart(2, '0')}-${String(yesterday.getDate()).padStart(2, '0')}`;
  if (due === yes) return 'вчера';
  return new Date(due).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
}

function formatMinutes(min) {
  if (!min) return '';
  if (min < 60) return min + ' мин';
  const h = Math.floor(min / 60), m = min % 60;
  return m ? `${h} ч ${m} мин` : `${h} ч`;
}

function toast(msg, type = 'success') {
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.textContent = msg;
  $('#toast-container').appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity .3s'; }, 2500);
  setTimeout(() => el.remove(), 2900);
}

/* ---------- Экраны ---------- */
function showAuth() { $('#auth-screen').classList.remove('hidden'); $('#app-screen').classList.add('hidden'); }
function showApp() { $('#auth-screen').classList.add('hidden'); $('#app-screen').classList.remove('hidden'); }

function logout() {
  API.clearToken();
  state.user = null;
  state.tasks = [];
  showAuth();
}

window.addEventListener('auth:expired', () => { toast('Сессия истекла, войдите снова', 'error'); logout(); });

/* ---------- Авторизация ---------- */
$('#tab-login').addEventListener('click', () => switchTab('login'));
$('#tab-register').addEventListener('click', () => switchTab('register'));

function switchTab(tab) {
  $('#tab-login').classList.toggle('active', tab === 'login');
  $('#tab-register').classList.toggle('active', tab === 'register');
  $('#form-login').classList.toggle('hidden', tab !== 'login');
  $('#form-register').classList.toggle('hidden', tab !== 'register');
  $('#login-error').classList.add('hidden');
  $('#register-error').classList.add('hidden');
}

$('#form-login').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = $('#login-error');
  errEl.classList.add('hidden');
  try {
    const data = await API.login($('#login-username').value.trim(), $('#login-password').value);
    API.setToken(data.access_token);
    state.user = await API.me();
    enterApp();
  } catch (ex) {
    errEl.textContent = ex.message;
    errEl.classList.remove('hidden');
  }
});

$('#form-register').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = $('#register-error');
  errEl.classList.add('hidden');
  try {
    await API.register($('#reg-username').value.trim(), $('#reg-email').value.trim(), $('#reg-password').value);
    // сразу логинимся
    const data = await API.login($('#reg-username').value.trim(), $('#reg-password').value);
    API.setToken(data.access_token);
    state.user = await API.me();
    toast('Аккаунт создан. Добро пожаловать! 🎉');
    enterApp();
  } catch (ex) {
    errEl.textContent = ex.message;
    errEl.classList.remove('hidden');
  }
});

$('#btn-logout').addEventListener('click', logout);

function enterApp() {
  $('#user-name').textContent = '👋 ' + state.user.username;
  showApp();
  loadTasks();
  loadStats();
}

/* ---------- Задачи ---------- */
async function loadTasks() {
  const opts = { search: state.search, sort: state.sort };
  if (state.filter === 'active') opts.completed = false;
  else if (state.filter === 'done') opts.completed = true;
  else if (state.filter === 'overdue') { opts.completed = false; opts.overdue = true; }
  try {
    state.tasks = await API.listTasks(opts);
    renderTasks();
  } catch (ex) { toast(ex.message, 'error'); }
}

async function loadStats() {
  try {
    const s = await API.stats();
    $('#stat-total').textContent = s.total;
    $('#stat-active').textContent = s.active;
    $('#stat-done').textContent = s.done;
    $('#stat-overdue').textContent = s.overdue;
    $('#stat-planned').textContent = formatMinutes(s.planned_minutes) || '—';
    $('#clear-done-wrap').classList.toggle('hidden', s.done === 0);
  } catch (ex) { /* не критично */ }
}

function refreshAll() { loadTasks(); loadStats(); }

function renderTasks() {
  const list = $('#task-list');
  list.innerHTML = '';
  $('#empty-state').classList.toggle('hidden', state.tasks.length !== 0);

  for (const t of state.tasks) {
    const item = document.createElement('div');
    const overdue = isOverdue(t);
    item.className = 'task-item' + (t.completed ? ' done' : '') + (overdue ? ' overdue' : '') + ' ' + (PRIORITY_META[t.priority]?.cls || '');
    item.innerHTML = `
      <button class="task-check ${t.completed ? 'checked' : ''}" title="Отметить" data-action="toggle">
        <svg viewBox="0 0 24 24"><path d="M4 12l5 5L20 6"/></svg>
      </button>
      <div class="task-body">
        <div class="task-title">${escapeHtml(t.title)}</div>
        ${t.description ? `<div class="task-desc">${escapeHtml(t.description)}</div>` : ''}
        <div class="task-meta">
          <span class="badge ${PRIORITY_META[t.priority]?.cls || ''}">${PRIORITY_META[t.priority]?.label || t.priority}</span>
          ${t.due_date ? `<span class="badge badge-due ${overdue ? 'badge-overdue' : ''}">📅 ${formatDue(t.due_date)}</span>` : ''}
          ${t.duration_minutes ? `<span class="badge badge-time">⏱ ${formatMinutes(t.duration_minutes)}</span>` : ''}
          <span class="task-date">создано ${formatDate(t.created_at)}</span>
        </div>
      </div>
      <div class="task-actions">
        <button class="icon-btn edit" title="Редактировать" data-action="edit">
          <svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
        </button>
        <button class="icon-btn del" title="Удалить" data-action="delete">
          <svg viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 14h10l1-14"/></svg>
        </button>
      </div>`;

    item.querySelector('[data-action="toggle"]').addEventListener('click', async () => {
      try {
        const wasDone = t.completed;
        const updated = await API.toggleTask(t.id);
        if (state.filter !== 'all') {
          loadTasks(); // при активном фильтре задача может "уйти" из списка
        } else {
          const idx = state.tasks.findIndex(x => x.id === t.id);
          if (idx >= 0) state.tasks[idx] = updated;
          renderTasks();
        }
        loadStats();
        if (!wasDone && updated.completed) celebrate(updated);
      } catch (ex) { toast(ex.message, 'error'); }
    });

    item.querySelector('[data-action="edit"]').addEventListener('click', () => openEditModal(t));

    item.querySelector('[data-action="delete"]').addEventListener('click', async () => {
      if (!confirm('Удалить задачу «' + t.title + '»?')) return;
      try {
        await API.deleteTask(t.id);
        state.tasks = state.tasks.filter(x => x.id !== t.id);
        renderTasks();
        loadStats();
        toast('Задача удалена');
      } catch (ex) { toast(ex.message, 'error'); }
    });

    list.appendChild(item);
  }
}

/* Конфетти + звук при выполнении задачи 🎉 */
function celebrate(task) {
  confettiBurst();
  playDing();
  const leftActive = state.tasks.filter(x => !x.completed && x.id !== task.id).length;
  if (leftActive === 0) toast('Все задачи выполнены! Ты машина! 🏆');
}

function confettiBurst() {
  const colors = ['#6c5ce7', '#00b894', '#fdcb6e', '#e17055', '#0984e3', '#e84393'];
  for (let i = 0; i < 26; i++) {
    const p = document.createElement('div');
    p.className = 'confetti';
    p.style.left = (45 + Math.random() * 10) + 'vw';
    p.style.top = '35vh';
    p.style.background = colors[i % colors.length];
    p.style.setProperty('--dx', (Math.random() * 2 - 1) * 40 + 'vw');
    p.style.setProperty('--dy', (30 + Math.random() * 45) + 'vh');
    p.style.setProperty('--rot', Math.random() * 720 + 'deg');
    p.style.animationDelay = (Math.random() * 0.15) + 's';
    document.body.appendChild(p);
    setTimeout(() => p.remove(), 1600);
  }
}

let audioCtx = null;
function playDing() {
  try {
    audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    const o = audioCtx.createOscillator(), g = audioCtx.createGain();
    o.type = 'sine';
    o.frequency.setValueAtTime(880, audioCtx.currentTime);
    o.frequency.exponentialRampToValueAtTime(1320, audioCtx.currentTime + 0.12);
    g.gain.setValueAtTime(0.15, audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.35);
    o.connect(g); g.connect(audioCtx.destination);
    o.start(); o.stop(audioCtx.currentTime + 0.4);
  } catch (e) { /* аудио недоступно — не страшно */ }
}

/* ---------- Добавление ---------- */
$('#toggle-desc').addEventListener('click', () => {
  const box = $('#add-details');
  box.classList.toggle('hidden');
  $('#toggle-desc').textContent = box.classList.contains('hidden')
    ? '＋ детали: описание, срок, время'
    : '－ скрыть детали';
  if (!box.classList.contains('hidden')) $('#new-desc').focus();
});

$('#form-add').addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = $('#new-title').value.trim();
  if (!title) return;
  const payload = {
    title,
    description: $('#new-desc').value.trim() || null,
    priority: $('#new-priority').value,
    due_date: $('#new-due').value || null,
    duration_minutes: $('#new-duration').value ? Number($('#new-duration').value) : null,
  };
  try {
    await API.createTask(payload);
    $('#new-title').value = '';
    $('#new-desc').value = '';
    $('#new-due').value = '';
    $('#new-duration').value = '';
    $('#new-priority').value = 'medium';
    await refreshAll();
    toast('Задача добавлена ✨');
  } catch (ex) { toast(ex.message, 'error'); }
});

/* ---------- Фильтры, сортировка, поиск ---------- */
document.querySelectorAll('.chip').forEach((chip) => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    state.filter = chip.dataset.filter;
    loadTasks();
  });
});

$('#sort-select').addEventListener('change', (e) => { state.sort = e.target.value; loadTasks(); });

let searchTimer = null;
$('#search-input').addEventListener('input', (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { state.search = e.target.value.trim(); loadTasks(); }, 300);
});

/* ---------- Очистка выполненных ---------- */
$('#btn-clear-done').addEventListener('click', async () => {
  if (!confirm('Удалить все выполненные задачи?')) return;
  try {
    const res = await API.deleteCompleted();
    toast(`Удалено выполненных: ${res.deleted} 🧹`);
    refreshAll();
  } catch (ex) { toast(ex.message, 'error'); }
});

/* ---------- Модалка редактирования ---------- */
function openEditModal(task) {
  state.editingId = task.id;
  $('#edit-title').value = task.title;
  $('#edit-desc').value = task.description || '';
  $('#edit-priority').value = task.priority || 'medium';
  $('#edit-due').value = task.due_date || '';
  $('#edit-duration').value = task.duration_minutes || '';
  $('#edit-modal').classList.remove('hidden');
  $('#edit-title').focus();
}

function closeEditModal() { $('#edit-modal').classList.add('hidden'); state.editingId = null; }

$('#edit-cancel').addEventListener('click', closeEditModal);
$('#edit-modal').addEventListener('click', (e) => { if (e.target.id === 'edit-modal') closeEditModal(); });
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !$('#edit-modal').classList.contains('hidden')) closeEditModal();
});

$('#edit-save').addEventListener('click', async () => {
  const title = $('#edit-title').value.trim();
  if (!title) { toast('Название не может быть пустым', 'error'); return; }
  const payload = {
    title,
    description: $('#edit-desc').value.trim() || null,
    priority: $('#edit-priority').value,
    due_date: $('#edit-due').value || null,
    duration_minutes: $('#edit-duration').value ? Number($('#edit-duration').value) : null,
  };
  try {
    await API.updateTask(state.editingId, payload);
    closeEditModal();
    await refreshAll();
    toast('Изменения сохранены');
  } catch (ex) { toast(ex.message, 'error'); }
});

/* ---------- Старт ---------- */
(async function init() {
  if (API.getToken()) {
    try {
      state.user = await API.me();
      enterApp();
      return;
    } catch (e) { API.clearToken(); }
  }
  showAuth();
})();
