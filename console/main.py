"""
Главный модуль ToDo-приложения.
Содержит меню и пользовательский интерфейс.
"""
from task import add_task, show_tasks, delete_task, toggle_task


def main() -> None:
    tasks: list = []

    while True:
        print("\n=== ToDo ===")
        print("1. Добавить задачу")
        print("2. Показать задачи")
        print("3. Удалить задачу")
        print("4. Изменить статус")
        print("5. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            title = input("Введите задачу: ")
            try:
                add_task(tasks, title)
                print("Задача добавлена.")
            except (TypeError, ValueError) as error:
                print(f"Ошибка: {error}")

        elif choice == "2":
            show_tasks(tasks)

        elif choice == "3":
            show_tasks(tasks)
            try:
                index = int(input("Номер задачи: ")) - 1
                delete_task(tasks, index)
            except ValueError:
                print("Введите число.")

        elif choice == "4":
            show_tasks(tasks)
            try:
                index = int(input("Номер задачи: ")) - 1
                toggle_task(tasks, index)
            except ValueError:
                print("Введите число.")

        elif choice == "5":
            print("До свидания!")
            break

        else:
            print("Неизвестная команда.")


if __name__ == "__main__":
    main()