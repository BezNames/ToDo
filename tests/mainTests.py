"""
Полный набор тестов для ToDo-приложения.
Покрывает 100% требований спецификации.
"""
import pytest
from task import add_task, show_tasks, delete_task, toggle_task


# ============================================================
# 1. ADD_TASK — успешное добавление
# ============================================================

@pytest.mark.parametrize("raw, expected", [
    ("Учиться",            "Учиться"),
    (" Проект ",           "Проект"),
    ("Разобрать тесты",    "Разобрать тесты"),
    ("   foo   bar   ",    "foo   bar"),
    ("\t\nПроект\n\t",     "Проект"),
    ("a",                  "a"),
])
def test_add_task_valid(raw, expected):
    tasks = []
    add_task(tasks, raw)
    assert len(tasks) == 1
    assert tasks[0]["title"] == expected
    assert tasks[0]["completed"] is False


def test_add_task_structure():
    tasks = []
    add_task(tasks, "Тест")
    task = tasks[0]
    assert set(task.keys()) == {"title", "completed"}
    assert isinstance(task["title"], str)
    assert isinstance(task["completed"], bool)


def test_add_task_multiple():
    tasks = []
    add_task(tasks, "Первая")
    add_task(tasks, " Вторая ")
    add_task(tasks, "Третья")
    assert len(tasks) == 3
    assert [t["title"] for t in tasks] == ["Первая", "Вторая", "Третья"]


def test_add_task_preserves_existing():
    tasks = [{"title": "Старая", "completed": True}]
    add_task(tasks, "Новая")
    assert len(tasks) == 2
    assert tasks[0] == {"title": "Старая", "completed": True}
    assert tasks[1] == {"title": "Новая", "completed": False}


# ============================================================
# 2. ADD_TASK — ValueError (пустая строка после strip)
# ============================================================

@pytest.mark.parametrize("bad", [
    "",
    " ",
    "     ",
    "\t",
    "\n",
    "\t\n",
    "   \t\n   ",
    "\r\n",
    "\xa0\xa0",
])
def test_add_task_empty_after_strip_raises_valueerror(bad):
    tasks = [{"title": "X", "completed": False}]
    with pytest.raises(ValueError, match="пустым"):
        add_task(tasks, bad)
    assert len(tasks) == 1
    assert tasks[0]["title"] == "X"


def test_add_task_error_does_not_modify_existing():
    tasks = [{"title": "Учиться", "completed": False}]
    with pytest.raises(ValueError):
        add_task(tasks, "   ")
    assert tasks == [{"title": "Учиться", "completed": False}]


# ============================================================
# 3. ADD_TASK — TypeError (не строка)
# ============================================================

@pytest.mark.parametrize("bad", [
    None,
    123,
    12.5,
    True,
    False,
    [],
    {},
    ("a", "b"),
    b"bytes",
])
def test_add_task_wrong_type_raises_typeerror(bad):
    tasks = [{"title": "X", "completed": False}]
    with pytest.raises(TypeError, match="строкой"):
        add_task(tasks, bad)
    assert len(tasks) == 1
    assert tasks[0]["title"] == "X"


# ============================================================
# 4. DELETE_TASK
# ============================================================

def test_delete_first_task():
    tasks = [
        {"title": "Первая", "completed": False},
        {"title": "Вторая", "completed": False},
    ]
    delete_task(tasks, 0)
    assert tasks == [{"title": "Вторая", "completed": False}]


def test_delete_last_task():
    tasks = [
        {"title": "Первая", "completed": False},
        {"title": "Вторая", "completed": False},
    ]
    delete_task(tasks, 1)
    assert tasks == [{"title": "Первая", "completed": False}]


def test_delete_middle_task():
    tasks = [
        {"title": "Первая", "completed": False},
        {"title": "Вторая", "completed": False},
        {"title": "Третья", "completed": False},
    ]
    delete_task(tasks, 1)
    assert [t["title"] for t in tasks] == ["Первая", "Третья"]


def test_delete_only_task():
    tasks = [{"title": "Учиться", "completed": False}]
    delete_task(tasks, 0)
    assert tasks == []


def test_delete_invalid_large_index():
    tasks = [{"title": "Учиться", "completed": False}]
    delete_task(tasks, 10)
    assert tasks == [{"title": "Учиться", "completed": False}]


def test_delete_negative_index():
    tasks = [{"title": "Учиться", "completed": False}]
    delete_task(tasks, -1)
    assert tasks == [{"title": "Учиться", "completed": False}]


def test_delete_from_empty_list():
    tasks = []
    delete_task(tasks, 0)
    assert tasks == []


# ============================================================
# 5. TOGGLE_TASK
# ============================================================

def test_toggle_false_to_true():
    tasks = [{"title": "Учиться", "completed": False}]
    toggle_task(tasks, 0)
    assert tasks[0]["completed"] is True


def test_toggle_true_to_false():
    tasks = [{"title": "Учиться", "completed": True}]
    toggle_task(tasks, 0)
    assert tasks[0]["completed"] is False


def test_toggle_twice_returns_original():
    tasks = [{"title": "Учиться", "completed": False}]
    toggle_task(tasks, 0)
    toggle_task(tasks, 0)
    assert tasks[0]["completed"] is False


def test_toggle_first_task():
    tasks = [
        {"title": "Первая", "completed": False},
        {"title": "Вторая", "completed": False},
    ]
    toggle_task(tasks, 0)
    assert tasks[0]["completed"] is True
    assert tasks[1]["completed"] is False


def test_toggle_last_task():
    tasks = [
        {"title": "Первая", "completed": False},
        {"title": "Вторая", "completed": False},
    ]
    toggle_task(tasks, 1)
    assert tasks[0]["completed"] is False
    assert tasks[1]["completed"] is True


def test_toggle_invalid_large_index():
    tasks = [{"title": "Учиться", "completed": False}]
    toggle_task(tasks, 10)
    assert tasks[0]["completed"] is False


def test_toggle_negative_index():
    tasks = [{"title": "Учиться", "completed": False}]
    toggle_task(tasks, -1)
    assert tasks[0]["completed"] is False


def test_toggle_empty_list():
    tasks = []
    toggle_task(tasks, 0)
    assert tasks == []


# ============================================================
# 6. SHOW_TASKS
# ============================================================

def test_show_empty_tasks(capsys):
    tasks = []
    show_tasks(tasks)
    captured = capsys.readouterr()
    assert "Список задач пуст." in captured.out


def test_show_uncompleted_task(capsys):
    tasks = [{"title": "Учиться", "completed": False}]
    show_tasks(tasks)
    captured = capsys.readouterr()
    assert "Учиться" in captured.out
    assert "[ ]" in captured.out


def test_show_completed_task(capsys):
    tasks = [{"title": "Учиться", "completed": True}]
    show_tasks(tasks)
    captured = capsys.readouterr()
    assert "Учиться" in captured.out
    assert "[✓]" in captured.out


def test_show_multiple_tasks(capsys):
    tasks = [
        {"title": "Учиться", "completed": False},
        {"title": "Работать", "completed": True},
        {"title": "Отдыхать", "completed": False},
    ]
    show_tasks(tasks)
    captured = capsys.readouterr()
    assert "Учиться" in captured.out
    assert "Работать" in captured.out
    assert "Отдыхать" in captured.out


def test_show_tasks_has_correct_numbers(capsys):
    tasks = [
        {"title": "Первая", "completed": False},
        {"title": "Вторая", "completed": False},
        {"title": "Третья", "completed": False},
    ]
    show_tasks(tasks)
    captured = capsys.readouterr()
    assert "1." in captured.out
    assert "2." in captured.out
    assert "3." in captured.out


def test_show_completed_and_uncompleted(capsys):
    tasks = [
        {"title": "Готово", "completed": True},
        {"title": "Не готово", "completed": False},
    ]
    show_tasks(tasks)
    captured = capsys.readouterr()
    assert "[✓] Готово" in captured.out
    assert "[ ] Не готово" in captured.out