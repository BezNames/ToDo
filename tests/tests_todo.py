import pytest

from task import add_task, show_tasks, delete_task, toggle_task


# ============================================================
# ADD_TASK
# ============================================================

def test_add_normal_task():
    tasks = []

    add_task(tasks, "Учиться")

    assert tasks == [
        {"title": "Учиться", "completed": False}
    ]


def test_add_task_strips_leading_spaces():
    tasks = []

    add_task(tasks, "   Учиться")

    assert tasks[0]["title"] == "Учиться"


def test_add_task_strips_trailing_spaces():
    tasks = []

    add_task(tasks, "Учиться   ")

    assert tasks[0]["title"] == "Учиться"


def test_add_task_strips_spaces_both_sides():
    tasks = []

    add_task(tasks, "   Проект   ")

    assert tasks[0]["title"] == "Проект"


def test_add_task_preserves_internal_spaces():
    tasks = []

    add_task(tasks, "Разобрать тесты")

    assert tasks[0]["title"] == "Разобрать тесты"


def test_add_multiple_tasks():
    tasks = []

    add_task(tasks, "Первая")
    add_task(tasks, "Вторая")
    add_task(tasks, "Третья")

    assert len(tasks) == 3


def test_new_task_is_not_completed():
    tasks = []

    add_task(tasks, "Учиться")

    assert tasks[0]["completed"] is False


@pytest.mark.parametrize("title", [
    "",
    " ",
    "     ",
    "\t",
    "\n",
    "\t\n",
])
def test_add_task_rejects_empty_titles(title):
    tasks = []

    with pytest.raises(ValueError):
        add_task(tasks, title)

    assert tasks == []


@pytest.mark.parametrize("title", [
    None,
    123,
    12.5,
    True,
    [],
    {},
])
def test_add_task_rejects_wrong_types(title):
    tasks = []

    with pytest.raises(TypeError):
        add_task(tasks, title)

    assert tasks == []


def test_add_task_error_does_not_modify_existing_tasks():
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    with pytest.raises(ValueError):
        add_task(tasks, "   ")

    assert tasks == [
        {"title": "Учиться", "completed": False}
    ]


# ============================================================
# DELETE_TASK
# ============================================================

def test_delete_first_task():
    tasks = [
        {"title": "Первая", "completed": False},
        {"title": "Вторая", "completed": False},
    ]

    delete_task(tasks, 0)

    assert tasks == [
        {"title": "Вторая", "completed": False}
    ]


def test_delete_last_task():
    tasks = [
        {"title": "Первая", "completed": False},
        {"title": "Вторая", "completed": False},
    ]

    delete_task(tasks, 1)

    assert tasks == [
        {"title": "Первая", "completed": False}
    ]


def test_delete_middle_task():
    tasks = [
        {"title": "Первая", "completed": False},
        {"title": "Вторая", "completed": False},
        {"title": "Третья", "completed": False},
    ]

    delete_task(tasks, 1)

    assert [task["title"] for task in tasks] == [
        "Первая",
        "Третья",
    ]


def test_delete_only_task():
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    delete_task(tasks, 0)

    assert tasks == []


def test_delete_invalid_large_index():
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    delete_task(tasks, 10)

    assert tasks == [
        {"title": "Учиться", "completed": False}
    ]


def test_delete_negative_index():
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    delete_task(tasks, -1)

    # По текущему контракту отрицательный индекс недопустим
    assert tasks == [
        {"title": "Учиться", "completed": False}
    ]


def test_delete_from_empty_list():
    tasks = []

    delete_task(tasks, 0)

    assert tasks == []


# ============================================================
# TOGGLE_TASK
# ============================================================

def test_toggle_false_to_true():
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    toggle_task(tasks, 0)

    assert tasks[0]["completed"] is True


def test_toggle_true_to_false():
    tasks = [
        {"title": "Учиться", "completed": True}
    ]

    toggle_task(tasks, 0)

    assert tasks[0]["completed"] is False


def test_toggle_twice_returns_original_status():
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

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
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    toggle_task(tasks, 10)

    assert tasks[0]["completed"] is False


def test_toggle_negative_index():
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    toggle_task(tasks, -1)

    assert tasks[0]["completed"] is False


def test_toggle_empty_list():
    tasks = []

    toggle_task(tasks, 0)

    assert tasks == []


# ============================================================
# SHOW_TASKS
# ============================================================

def test_show_empty_tasks(capsys):
    tasks = []

    show_tasks(tasks)

    captured = capsys.readouterr()

    assert "Список задач пуст." in captured.out


def test_show_uncompleted_task(capsys):
    tasks = [
        {"title": "Учиться", "completed": False}
    ]

    show_tasks(tasks)

    captured = capsys.readouterr()

    assert "Учиться" in captured.out
    assert "[ ]" in captured.out


def test_show_completed_task(capsys):
    tasks = [
        {"title": "Учиться", "completed": True}
    ]

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


def test_show_completed_and_uncompleted_tasks(capsys):
    tasks = [
        {"title": "Готово", "completed": True},
        {"title": "Не готово", "completed": False},
    ]

    show_tasks(tasks)

    captured = capsys.readouterr()

    assert "[✓] Готово" in captured.out
    assert "[ ] Не готово" in captured.out