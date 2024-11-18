import os
import subprocess
import csv
import sys


# Вспомогательные функции для отладки
def debug_message(message):
    """Выводит отладочное сообщение."""
    print(f"[DEBUG] {message}")


def debug_path(path):
    """Выводит информацию о пути для диагностики."""
    print(f"[DEBUG] Путь: {path}")
    print(f"Абсолютный путь: {os.path.abspath(path)}")
    print(f"Существует: {os.path.exists(path)}")
    print(f"Кодировка: {os.fsencode(path)}")


# Основные функции
def load_config(config_path='config.csv'):
    """Загружает конфигурацию из CSV."""
    debug_message("Загрузка конфигурации...")
    config = {}
    try:
        with open(config_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 2:
                    config[row[0]] = row[1]
        debug_message(f"Конфигурация загружена: {config}")
    except FileNotFoundError:
        print(f"[ERROR] Файл конфигурации {config_path} не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Ошибка при чтении конфигурации: {e}")
        sys.exit(1)
    return config


def run_command(command, cwd=None):
    """Выполняет команду в subprocess и возвращает результат."""
    debug_message(f"Выполнение команды: {' '.join(command)}")
    if cwd:
        debug_path(cwd)
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"[ERROR] Команда завершилась с ошибкой: {result.stderr}")
            sys.exit(1)
        return result.stdout.strip()
    except Exception as e:
        print(f"[ERROR] Ошибка при выполнении команды: {e}")
        sys.exit(1)


def get_commits(repo_path):
    """Получает список коммитов из репозитория."""
    debug_message("Получение списка коммитов...")
    return run_command(['git', 'log', '--oneline'], repo_path).splitlines()


def find_dependencies(file_hash, repo_path):
    """Находит зависимости файла."""
    debug_message(f"Поиск зависимостей для хеша {file_hash}...")
    commits = get_commits(repo_path)
    debug_message(f"Найдено {len(commits)} коммитов.")
    for commit in commits:
        if file_hash in commit:
            debug_message(f"Коммит найден: {commit}")
            return [f"dependency_{i}" for i in range(3)]  # Заглушка: заменить реальной логикой.
    print(f"[ERROR] Не найдено коммитов с хешем {file_hash}.")
    sys.exit(1)


def generate_puml_file(dependencies, puml_path):
    """Генерирует файл PlantUML."""
    debug_message(f"Генерация PlantUML файла: {puml_path}")
    try:
        with open(puml_path, mode='w', encoding='utf-8') as puml_file:
            puml_file.write("@startuml\n")
            for dep in dependencies:
                puml_file.write(f"{dep} -> {dep}_child\n")
            puml_file.write("@enduml\n")
        debug_message("Файл PlantUML успешно создан.")
    except Exception as e:
        print(f"[ERROR] Ошибка при создании PlantUML файла: {e}")
        sys.exit(1)


def generate_png(puml_path, png_path, plantuml_path):
    """Генерирует PNG файл из PlantUML."""
    debug_message(f"Генерация PNG из PlantUML: {puml_path} -> {png_path}")
    run_command(['java', '-jar', plantuml_path, puml_path, '-o', os.path.dirname(png_path)])
    debug_message("PNG файл успешно создан.")


def visualize_dependencies():
    """Основная функция визуализации зависимостей."""
    debug_message("Запуск визуализации...")
    config = load_config()
    repo_path = config['repo_path']
    file_hash = config['file_hash']
    puml_path = config['puml_output_path']
    png_path = config['png_output_path']
    plantuml_path = config['plantuml_path']

    debug_message("Проверка путей...")
    debug_path(repo_path)
    debug_path(os.path.dirname(puml_path))
    debug_path(plantuml_path)

    dependencies = find_dependencies(file_hash, repo_path)
    generate_puml_file(dependencies, puml_path)
    generate_png(puml_path, png_path, plantuml_path)
    debug_message("Визуализация завершена.")


if __name__ == "__main__":
    visualize_dependencies()
