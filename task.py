"""
Модуль бизнес-логики ToDo-приложения.
Содержит функции для работы со списком задач.
Не содержит пользовательского интерфейса.
"""


def add_task(tasks: list, title: str) -> None:
    """Добавить задачу в список."""
    if not isinstance(title, str):
        raise TypeError("название задачи должно быть строкой.")
    title = title.strip()
    if not title:
        raise ValueError("название задачи не может быть пустым.")
    tasks.append({
        "title": title,
        "completed": False
    })


def show_tasks(tasks: list) -> None:
    """Вывести список задач."""
    if not tasks:
        print("Список задач пуст.")
        return
    for i, task in enumerate(tasks, 1):
        status = "✓" if task["completed"] else " "
        print(f"{i}. [{status}] {task['title']}")


def delete_task(tasks: list, index: int) -> None:
    """Удалить задачу по индексу."""
    if 0 <= index < len(tasks):
        tasks.pop(index)
        print("Задача удалена.")
    else:
        print("Неверный номер задачи.")


def toggle_task(tasks: list, index: int) -> None:
    """Изменить статус задачи на противоположный."""
    if 0 <= index < len(tasks):
        tasks[index]["completed"] = not tasks[index]["completed"]
        print("Статус задачи изменён.")
    else:
        print("Неверный номер задачи.")