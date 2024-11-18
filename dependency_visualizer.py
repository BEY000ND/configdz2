import csv
import subprocess
import os

def load_config(config_path):
    """
    Загружает параметры из конфигурационного файла CSV.
    Возвращает словарь с параметрами.
    """
    config = {}
    with open(config_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:  # Убедимся, что строка содержит два элемента (ключ и значение)
                key, value = row
                config[key.strip()] = value.strip()
            else:
                print(f"Некорректная строка конфигурации: {row}")
    return config

def run_git_log(repo_path, file_hash):
    """
    Запускает команду git log для получения коммитов, связанных с файлом.
    """
    try:
        # Запускаем команду git log, чтобы получить информацию о коммитах
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%H %s', '--', file_hash],
            cwd=repo_path, text=True, capture_output=True, check=True
        )
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении git log: {e}")
        return []

def generate_plantuml_graph(commits, puml_output_path):
    """
    Генерирует граф зависимостей в формате PlantUML на основе коммитов.
    """
    try:
        with open(puml_output_path, 'w', encoding='utf-8') as puml_file:
            puml_file.write("@startuml\n")
            for commit in commits:
                commit_hash, commit_message = commit.split(" ", 1)
                puml_file.write(f"'{commit_hash}': {commit_message}\n")
            puml_file.write("@enduml\n")
        print(f"Граф сохранён в {puml_output_path}")
    except Exception as e:
        print(f"Ошибка при записи файла PlantUML: {e}")

def generate_png_from_puml(puml_output_path, png_output_path, plantuml_path):
    """
    Генерирует PNG изображение из файла PlantUML с использованием PlantUML.
    """
    try:
        # Запускаем PlantUML для конвертации puml в png
        subprocess.run(
            ['java', '-jar', plantuml_path, puml_output_path],
            check=True
        )
        os.rename(puml_output_path.replace('.puml', '.png'), png_output_path)
        print(f"PNG граф сохранён в {png_output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении PlantUML: {e}")
    except FileNotFoundError as e:
        print(f"Не найден файл для генерации PNG: {e}")

def main():
    # Путь к конфигурации
    config_path = "config.csv"
    
    config = load_config(config_path)
    
    if not config:
        print("Ошибка: Параметры конфигурации отсутствуют!")
        return
    
    print(f"Конфигурация: {config}")

    repo_path = config.get("repo_path")
    file_hash = config.get("file_hash")
    puml_output_path = config.get("puml_output_path")
    png_output_path = config.get("png_output_path")
    plantuml_path = config.get("plantuml_path")

    # Проверяем, что все параметры существуют
    if not repo_path or not file_hash or not puml_output_path or not png_output_path or not plantuml_path:
        print("Ошибка: Параметры конфигурации отсутствуют!")
        return

    print(f"Путь репозитория: {repo_path}")
    print(f"Хеш файла: {file_hash}")
    print(f"Путь для вывода PlantUML: {puml_output_path}")
    print(f"Путь для вывода PNG: {png_output_path}")
    print(f"Путь к PlantUML: {plantuml_path}")

    # Получаем коммиты из репозитория
    commits = run_git_log(repo_path, file_hash)
    
    if not commits:
        print("Не найдено зависимостей для данного файла.")
        return

    # Обрабатываем и генерируем граф PlantUML
    generate_plantuml_graph(commits, puml_output_path)

    # Генерируем PNG из графа PlantUML
    generate_png_from_puml(puml_output_path, png_output_path, plantuml_path)

if __name__ == "__main__":
    main()
