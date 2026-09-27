/* Обёртка над API: токен хранится в localStorage. */
const API = {
  tokenKey: 'todo_token',

  getToken() { return localStorage.getItem(this.tokenKey); },
  setToken(t) { localStorage.setItem(this.tokenKey, t); },
  clearToken() { localStorage.removeItem(this.tokenKey); },

  async request(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    const token = this.getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;

    const resp = await fetch(path, { ...options, headers });

    if (resp.status === 401 && !path.includes('/auth/')) {
      // токен протух — принудительный выход
      this.clearToken();
      window.dispatchEvent(new CustomEvent('auth:expired'));
      throw new Error('Сессия истекла, войдите снова');
    }

    if (resp.status === 204) return null;

    let data = null;
    try { data = await resp.json(); } catch (e) { /* пустой ответ */ }

    if (!resp.ok) {
      const detail = data && data.detail
        ? (typeof data.detail === 'string' ? data.detail : 'Некорректные данные')
        : 'Ошибка сервера';
      throw new Error(detail);
    }
    return data;
  },

  // Auth
  register(username, email, password) {
    return this.request('/api/auth/register', { method: 'POST', body: JSON.stringify({ username, email, password }) });
  },
  login(username, password) {
    return this.request('/api/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) });
  },
  me() { return this.request('/api/auth/me'); },

  // Tasks
  listTasks({ completed = null, search = '', priority = '', overdue = false, sort = 'created' } = {}) {
    const params = new URLSearchParams();
    if (completed !== null) params.set('completed', completed);
    if (search) params.set('search', search);
    if (priority) params.set('priority', priority);
    if (overdue) params.set('overdue', 'true');
    if (sort && sort !== 'created') params.set('sort', sort);
    const qs = params.toString();
    return this.request('/api/tasks' + (qs ? '?' + qs : ''));
  },
  stats() { return this.request('/api/tasks/stats'); },
  createTask(data) {
    return this.request('/api/tasks', { method: 'POST', body: JSON.stringify(data) });
  },
  updateTask(id, data) {
    return this.request('/api/tasks/' + id, { method: 'PUT', body: JSON.stringify(data) });
  },
  toggleTask(id) {
    return this.request('/api/tasks/' + id + '/toggle', { method: 'PATCH' });
  },
  deleteCompleted() {
    return this.request('/api/tasks/done', { method: 'DELETE' });
  },
  deleteTask(id) {
    return this.request('/api/tasks/' + id, { method: 'DELETE' });
  },
};
