import pytest

from Egor.task import add_task, show_tasks, delete_task, toggle_task


# ---------- add_task ----------

def test_add_normal_task():
    tasks = []

    add_task(tasks, "Учиться")

    assert tasks == [
        {"title": "Учиться", "completed": False}
    ]


def test_add_task_strips_spaces():
    tasks = []

    add_task(tasks, "   Проект   ")

    assert tasks[0]["title"] == "Проект"


def test_add_task_preserves_internal_spaces():
    tasks = []

    add_task(tasks, "Разобрать тесты")

    assert tasks[0]["title"] == "Разобрать тесты"


@pytest.mark.parametrize("title", [
    "",
    "     ",
    "\t",
    "\n",
])
def test_add_task_rejects_empty_title(title):
    tasks = []

    with pytest.raises(ValueError):
        add_task(tasks, title)

    assert tasks == []


def test_add_task_rejects_none():
    tasks = []

    with pytest.raises(TypeError):
        add_task(tasks, None)

    assert tasks == []


def test_add_task_rejects_wrong_type():
    tasks = []

    with pytest.raises(TypeError):
        add_task(tasks, 123)

    assert tasks == []


# ---------- delete_task ----------

def test_delete_task():
    tasks = [
        {"title": "Учиться", "completed": False},
        {"title": "Работать", "completed": False},
    ]

    delete_task(tasks, 0)

    assert len(tasks) == 1
    assert tasks[0]["title"] == "Работать"


def test_delete_invalid_index_does_not_change_tasks():
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    delete_task(tasks, 5)

    assert len(tasks) == 1


# ---------- toggle_task ----------

def test_toggle_task_to_completed():
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    toggle_task(tasks, 0)

    assert tasks[0]["completed"] is True


def test_toggle_task_to_not_completed():
    tasks = [
        {"title": "Учиться", "completed": True}
    ]

    toggle_task(tasks, 0)

    assert tasks[0]["completed"] is False


def test_toggle_invalid_index_does_not_change_tasks():
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    toggle_task(tasks, 5)

    assert tasks[0]["completed"] is False


# ---------- show_tasks ----------

def test_show_empty_tasks(capsys):
    tasks = []

    show_tasks(tasks)

    captured = capsys.readouterr()

    assert "Список задач пуст." in captured.out


def test_show_tasks(capsys):
    tasks = [
        {"title": "Учиться", "completed": False},
        {"title": "Работать", "completed": True},
    ]

    show_tasks(tasks)

    captured = capsys.readouterr()

    assert "Учиться" in captured.out
    assert "Работать" in captured.out
    assert "✓" in captured.out