/* Логика фронтенда ToDo */
const $ = (sel) => document.querySelector(sel);

const state = { user: null, tasks: [], filter: 'all', search: '', editingId: null };

/* ---------- Утилиты ---------- */
function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleString('ru-RU', { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' });
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
}

/* ---------- Задачи ---------- */
async function loadTasks() {
  const completed = state.filter === 'active' ? false : state.filter === 'done' ? true : null;
  try {
    state.tasks = await API.listTasks({ completed, search: state.search });
    renderTasks();
  } catch (ex) { toast(ex.message, 'error'); }
}

function renderTasks() {
  const list = $('#task-list');
  list.innerHTML = '';
  $('#empty-state').classList.toggle('hidden', state.tasks.length !== 0);

  for (const t of state.tasks) {
    const item = document.createElement('div');
    item.className = 'task-item' + (t.completed ? ' done' : '');
    item.innerHTML = `
      <button class="task-check ${t.completed ? 'checked' : ''}" title="Отметить" data-action="toggle">
        <svg viewBox="0 0 24 24"><path d="M4 12l5 5L20 6"/></svg>
      </button>
      <div class="task-body">
        <div class="task-title">${escapeHtml(t.title)}</div>
        ${t.description ? `<div class="task-desc">${escapeHtml(t.description)}</div>` : ''}
        <div class="task-date">создано ${formatDate(t.created_at)}</div>
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
        const updated = await API.toggleTask(t.id);
        if (state.filter !== 'all') {
          loadTasks(); // при активном фильтре задача может "уйти" из списка
        } else {
          const idx = state.tasks.findIndex(x => x.id === t.id);
          if (idx >= 0) state.tasks[idx] = updated;
          renderTasks();
        }
        updateStats();
      } catch (ex) { toast(ex.message, 'error'); }
    });

    item.querySelector('[data-action="edit"]').addEventListener('click', () => openEditModal(t));

    item.querySelector('[data-action="delete"]').addEventListener('click', async () => {
      if (!confirm('Удалить задачу «' + t.title + '»?')) return;
      try {
        await API.deleteTask(t.id);
        state.tasks = state.tasks.filter(x => x.id !== t.id);
        renderTasks();
        updateStats();
        toast('Задача удалена');
      } catch (ex) { toast(ex.message, 'error'); }
    });

    list.appendChild(item);
  }
  updateStats();
}

function updateStats() {
  // статистика считается по всем задачам пользователя независимо от фильтра
  const total = state.tasks.length;
  const done = state.tasks.filter(t => t.completed).length;
  $('#stat-total').textContent = total;
  $('#stat-done').textContent = done;
  $('#stat-active').textContent = total - done;
}

/* ---------- Добавление ---------- */
$('#toggle-desc').addEventListener('click', () => {
  const inp = $('#new-desc');
  inp.classList.toggle('hidden');
  $('#toggle-desc').textContent = inp.classList.contains('hidden') ? '＋ добавить описание' : '－ скрыть описание';
  if (!inp.classList.contains('hidden')) inp.focus();
});

$('#form-add').addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = $('#new-title').value.trim();
  if (!title) return;
  const desc = $('#new-desc').value.trim();
  try {
    await API.createTask(title, desc);
    $('#new-title').value = '';
    $('#new-desc').value = '';
    await loadTasks();
    toast('Задача добавлена ✨');
  } catch (ex) { toast(ex.message, 'error'); }
});

/* ---------- Фильтры и поиск ---------- */
document.querySelectorAll('.chip').forEach((chip) => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    state.filter = chip.dataset.filter;
    loadTasks();
  });
});

let searchTimer = null;
$('#search-input').addEventListener('input', (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { state.search = e.target.value.trim(); loadTasks(); }, 300);
});

/* ---------- Модалка редактирования ---------- */
function openEditModal(task) {
  state.editingId = task.id;
  $('#edit-title').value = task.title;
  $('#edit-desc').value = task.description || '';
  $('#edit-modal').classList.remove('hidden');
  $('#edit-title').focus();
}

function closeEditModal() { $('#edit-modal').classList.add('hidden'); state.editingId = null; }

$('#edit-cancel').addEventListener('click', closeEditModal);
$('#edit-modal').addEventListener('click', (e) => { if (e.target.id === 'edit-modal') closeEditModal(); });

$('#edit-save').addEventListener('click', async () => {
  const title = $('#edit-title').value.trim();
  if (!title) { toast('Название не может быть пустым', 'error'); return; }
  try {
    await API.updateTask(state.editingId, { title, description: $('#edit-desc').value.trim() || null });
    closeEditModal();
    await loadTasks();
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
