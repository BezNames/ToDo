"""Тесты API: регистрация, вход, CRUD задач, изоляция пользователей."""
PREFIX = "/api"


def register(client, username="alice", password="secret123"):
    return client.post(
        f"{PREFIX}/auth/register",
        json={"username": username, "email": f"{username}@test.com", "password": password},
    )


def login(client, username="alice", password="secret123"):
    return client.post(f"{PREFIX}/auth/login", json={"username": username, "password": password})


def auth_header(client, username="alice"):
    register(client, username)
    token = login(client, username).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------- health ----------

def test_health(client):
    assert client.get(f"{PREFIX}/health").json() == {"status": "ok"}


# ---------- auth ----------

def test_register_success(client):
    r = register(client)
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == "alice"
    assert "password" not in body and "password_hash" not in body


def test_register_duplicate(client):
    register(client)
    assert register(client).status_code == 409


def test_register_short_password(client):
    r = client.post(f"{PREFIX}/auth/register", json={
        "username": "bob", "email": "bob@test.com", "password": "123"})
    assert r.status_code == 422


def test_login_wrong_password(client):
    register(client)
    assert login(client, password="wrong").status_code == 401


def test_login_by_email(client):
    register(client)
    r = client.post(f"{PREFIX}/auth/login", json={"username": "alice@test.com", "password": "secret123"})
    assert r.status_code == 200


def test_me(client):
    headers = auth_header(client)
    r = client.get(f"{PREFIX}/auth/me", headers=headers)
    assert r.status_code == 200 and r.json()["username"] == "alice"


def test_me_unauthorized(client):
    assert client.get(f"{PREFIX}/auth/me").status_code == 401
    assert client.get(f"{PREFIX}/auth/me", headers={"Authorization": "Bearer bad"}).status_code == 401


# ---------- tasks ----------

def test_create_and_list_tasks(client):
    h = auth_header(client)
    r = client.post(f"{PREFIX}/tasks", json={"title": "Купить хлеб"}, headers=h)
    assert r.status_code == 201
    task = r.json()
    assert task["completed"] is False

    items = client.get(f"{PREFIX}/tasks", headers=h).json()
    assert len(items) == 1 and items[0]["title"] == "Купить хлеб"


def test_tasks_require_auth(client):
    assert client.get(f"{PREFIX}/tasks").status_code == 401
    assert client.post(f"{PREFIX}/tasks", json={"title": "x"}).status_code == 401


def test_toggle_task(client):
    h = auth_header(client)
    tid = client.post(f"{PREFIX}/tasks", json={"title": "t"}, headers=h).json()["id"]
    r = client.patch(f"{PREFIX}/tasks/{tid}/toggle", headers=h)
    assert r.json()["completed"] is True
    r = client.patch(f"{PREFIX}/tasks/{tid}/toggle", headers=h)
    assert r.json()["completed"] is False


def test_update_task(client):
    h = auth_header(client)
    tid = client.post(f"{PREFIX}/tasks", json={"title": "old"}, headers=h).json()["id"]
    r = client.put(f"{PREFIX}/tasks/{tid}", json={"title": "new", "completed": True}, headers=h)
    assert r.json()["title"] == "new" and r.json()["completed"] is True


def test_delete_task(client):
    h = auth_header(client)
    tid = client.post(f"{PREFIX}/tasks", json={"title": "del"}, headers=h).json()["id"]
    assert client.delete(f"{PREFIX}/tasks/{tid}", headers=h).status_code == 204
    assert client.get(f"{PREFIX}/tasks/{tid}", headers=h).status_code == 404


def test_search_and_filter(client):
    h = auth_header(client)
    client.post(f"{PREFIX}/tasks", json={"title": "Выучить Python"}, headers=h)
    client.post(f"{PREFIX}/tasks", json={"title": "Помыть посуду"}, headers=h)
    found = client.get(f"{PREFIX}/tasks?search=Python", headers=h).json()
    assert len(found) == 1
    client.patch(f"{PREFIX}/tasks/{found[0]['id']}/toggle", headers=h)
    done = client.get(f"{PREFIX}/tasks?completed=true", headers=h).json()
    assert len(done) == 1 and done[0]["title"] == "Выучить Python"


def test_tasks_isolated_between_users(client):
    h1 = auth_header(client, "alice")
    h2 = auth_header(client, "bob")
    tid = client.post(f"{PREFIX}/tasks", json={"title": "secret"}, headers=h1).json()["id"]
    # bob не видит задачу alice
    assert client.get(f"{PREFIX}/tasks", headers=h2).json() == []
    assert client.get(f"{PREFIX}/tasks/{tid}", headers=h2).status_code == 404
    assert client.delete(f"{PREFIX}/tasks/{tid}", headers=h2).status_code == 404


# ---------- Новые фичи: приоритет, срок, длительность, статистика ----------

def _create(client, H, **kw):
    payload = {"title": kw.pop("title", "Задача"), "description": None}
    payload.update(kw)
    r = client.post("/api/tasks", json=payload, headers=H)
    assert r.status_code == 201, r.text
    return r.json()


def test_task_defaults_and_fields(client):
    H = auth_header(client)
    t = _create(client, H, title="Купить хлеб")
    assert t["priority"] == "medium"
    assert t["due_date"] is None
    assert t["duration_minutes"] is None


def test_task_create_with_meta(client):
    H = auth_header(client)
    t = _create(client, H, title="Сделать уроки", priority="high",
               due_date="2030-01-15", duration_minutes=45)
    assert t["priority"] == "high"
    assert t["due_date"] == "2030-01-15"
    assert t["duration_minutes"] == 45


def test_invalid_priority_rejected(client):
    H = auth_header(client)
    r = client.post("/api/tasks", json={"title": "x", "priority": "ultra"}, headers=H)
    assert r.status_code == 422


def test_duration_bounds(client):
    H = auth_header(client)
    r = client.post("/api/tasks", json={"title": "x", "duration_minutes": 99999}, headers=H)
    assert r.status_code == 422


def test_sort_by_priority(client):
    H = auth_header(client)
    _create(client, H, title="низкая", priority="low")
    _create(client, H, title="высокая", priority="high")
    _create(client, H, title="обычная", priority="medium")
    r = client.get("/api/tasks", params={"sort": "priority"}, headers=H)
    titles = [t["title"] for t in r.json()]
    assert titles[:3] == ["высокая", "обычная", "низкая"] or set(titles[:3]) == {"высокая", "обычная", "низкая"}
    order = [t["priority"] for t in r.json() if t["title"] in ("высокая", "обычная", "низкая")]
    assert order == ["high", "medium", "low"]


def test_overdue_filter_and_stats(client):
    H = auth_header(client)
    _create(client, H, title="просрочена", due_date="2020-01-01", duration_minutes=60)
    _create(client, H, title="сегодня", due_date="2099-01-01", duration_minutes=30)
    done = _create(client, H, title="готова", duration_minutes=999)
    client.patch(f"/api/tasks/{done['id']}/toggle", headers=H)

    r = client.get("/api/tasks", params={"overdue": True, "completed": False}, headers=H)
    assert [t["title"] for t in r.json()] == ["просрочена"]

    s = client.get("/api/tasks/stats", headers=H).json()
    assert s["overdue"] >= 1
    assert s["planned_minutes"] >= 90  # 60 + 30 (без выполненной)
    assert s["total"] >= 3 and s["done"] >= 1


def test_delete_completed(client):
    H = auth_header(client)
    a = _create(client, H, title="a")
    b = _create(client, H, title="b")
    c = _create(client, H, title="c")
    client.patch(f"/api/tasks/{a['id']}/toggle", headers=H)
    client.patch(f"/api/tasks/{b['id']}/toggle", headers=H)

    r = client.delete("/api/tasks/done", headers=H)
    assert r.status_code == 200
    assert r.json()["deleted"] >= 2

    left = client.get("/api/tasks", headers=H).json()
    assert all(t["title"] != "a" for t in left)
