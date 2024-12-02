import os
import sqlite3

DB_PATH = "ege_tasks.db"
TASKS_FOLDER = "tasks_images"

def create_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_number INTEGER NOT NULL,
                variant INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                zip_path TEXT,
                correct_answer TEXT NOT NULL
            )
        """)
        print("База данных и таблица `tasks` успешно созданы (если их не было).")

def populate_database():

    tasks = [
        (1, ["ЕДБГИВАЖ", "18"], False),
        (2, ["zywx", "xzyw"], False),
        (3, ["М35", "736"], True),
        (4, ["27", "14"], False),
        (5, ["9", "4"], False),
        (6, ["50", "78"], False),
        (7, ["200", "8"], False),
        (8, ["2200", "ЛККР"], False),
        (9, ["1483", "1842"], True),
        (10, ["38", "6"], True),
        (11, ["19", "100"], False),
        (12, ["2112", "112"], False),
        (13, ["8192", "27"], False),
        (14, ["1345", "0"], False),
        (15, ["17", "75"], False),
        (16, ["32", "2024"], False),
        (17, ["74 433966217", "6243772 19992"], True),
        (18, ["358", "2167 718"], True),
        (19, ["12", "12"], False),
        (20, ["1011", "2122"], False),
        (21, ["9", "20"], False),
        (22, ["31", "39"], True),
        (23, ["57", "64"], False),
        (24, ["1004", "33"], True),
        (25, ["162139404 80148 1321399324 653188 1421396214 702618 1521393104 752048", "1008 1797092 48408867 1800 1156923"], False),
        (26, ["103 248", "7768 20"], True),
        (27, ["10738 30730 37522 51277", "NAN"], True)
    ]

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for task_number, answers, has_zip in tasks:
            for variant, correct_answer in enumerate(answers, start=1):
                image_path = os.path.join(TASKS_FOLDER, f"task{task_number}_{variant}.png")
                zip_path = os.path.join(TASKS_FOLDER, f"task{task_number}_{variant}.zip") if has_zip else None

                # Проверяем наличие файлов
                missing_files = []
                if not os.path.exists(image_path):
                    missing_files.append(f"Изображение ({image_path})")
                if has_zip and zip_path and not os.path.exists(zip_path):
                    missing_files.append(f"ZIP-архив ({zip_path})")

                if missing_files:
                    print(f"Пропущено задание {task_number} вариант {variant}: отсутствуют файлы: {', '.join(missing_files)}")
                    continue

                # Добавляем запись в базу данных
                cursor.execute("""
                    INSERT OR REPLACE INTO tasks (task_number, variant, image_path, zip_path, correct_answer)
                    VALUES (?, ?, ?, ?, ?)
                """, (task_number, variant, image_path, zip_path, correct_answer))
                print(f"Добавлено задание {task_number} вариант {variant} с ответом '{correct_answer}'.")

        conn.commit()
        print("Заполнение базы данных завершено.")

def get_task(task_number, variant):
    """
    :param task_number: Номер задания
    :param variant: Номер варианта
    :return: Словарь с данными задания или None, если не найдено
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT task_number, variant, image_path, zip_path, correct_answer
            FROM tasks
            WHERE task_number = ? AND variant = ?
        """, (task_number, variant))
        row = cursor.fetchone()
        if row:
            return {
                "task_number": row[0],
                "variant": row[1],
                "image_path": row[2],
                "zip_path": row[3],
                "correct_answer": row[4],
            }
        return None

def get_all_tasks():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT task_number, variant, image_path, zip_path, correct_answer
            FROM tasks
        """)
        rows = cursor.fetchall()
        return [
            {
                "task_number": row[0],
                "variant": row[1],
                "image_path": row[2],
                "zip_path": row[3],
                "correct_answer": row[4],
            }
            for row in rows
        ]

if __name__ == "__main__":
    create_database()
    populate_database()
    
    task = get_task(27, 1)
    if task:
        print(f"Найдено задание: {task}")
    else:
        print("Задание не найдено.")
