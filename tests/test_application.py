"""
Полный набор тестов для функции add_task().
Покрывает 100% ветвей и требований контракта из спецификации.
"""
import pytest
from Egor.task import add_task


# ============================================================
# 1. УСПЕШНОЕ ДОБАВЛЕНИЕ — ветка "корректная строка"
# ============================================================

@pytest.mark.parametrize("raw, expected", [
    ("Учиться",            "Учиться"),           # обычная строка
    (" Проект ",           "Проект"),             # пробелы по краям
    ("Разобрать тесты",    "Разобрать тесты"),    # пробелы внутри
    ("   foo   bar   ",    "foo   bar"),          # множественные внутренние
    ("\t\nПроект\n\t",     "Проект"),             # табы/переводы строк
    ("a",                  "a"),                  # один символ
])
def test_add_task_valid(raw, expected):
    tasks = []
    add_task(tasks, raw)

    assert len(tasks) == 1
    assert tasks[0]["title"] == expected
    assert tasks[0]["completed"] is False


def test_add_task_structure():
    """Структура объекта задачи соответствует контракту."""
    tasks = []
    add_task(tasks, "Тест")
    task = tasks[0]

    assert set(task.keys()) == {"title", "completed"}
    assert isinstance(task["title"], str)
    assert isinstance(task["completed"], bool)


def test_add_task_multiple():
    """Несколько задач добавляются последовательно."""
    tasks = []
    add_task(tasks, "Первая")
    add_task(tasks, " Вторая ")
    add_task(tasks, "Третья")

    assert len(tasks) == 3
    assert [t["title"] for t in tasks] == ["Первая", "Вторая", "Третья"]


def test_add_task_preserves_existing():
    """Новая задача добавляется к уже существующим, не затирая их."""
    tasks = [{"title": "Старая", "completed": True}]
    add_task(tasks, "Новая")

    assert len(tasks) == 2
    assert tasks[0] == {"title": "Старая", "completed": True}
    assert tasks[1] == {"title": "Новая", "completed": False}


# ============================================================
# 2. ValueError — ветка "пустая строка после strip()"
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
    "\xa0\xa0",          # non-breaking space — тоже whitespace
])
def test_add_task_empty_after_strip_raises_valueerror(bad):
    tasks = [{"title": "X", "completed": False}]
    with pytest.raises(ValueError, match="пустым"):
        add_task(tasks, bad)

    # Список НЕ изменился
    assert len(tasks) == 1
    assert tasks[0]["title"] == "X"


# ============================================================
# 3. TypeError — ветка "не строка"
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

    # Список НЕ изменился
    assert len(tasks) == 1
    assert tasks[0]["title"] == "X"