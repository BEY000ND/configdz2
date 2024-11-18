import os
import csv
import subprocess
import hashlib

def load_config(config_path):
    """Загрузка конфигурации из CSV файла."""
    config = {}
    try:
        with open(config_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                config[row[0]] = row[1]
    except Exception as e:
        print(f"Ошибка при чтении конфигурационного файла: {e}")
        exit(1)
    return config

def get_commit_files(repo_path, commit_hash):
    """Получение файлов, затронутых коммитом по его хешу с помощью Git."""
    try:
        # Выполняем команду git show, чтобы получить изменения в коммите
        result = subprocess.run(
            ["git", "show", "--name-only", "--oneline", commit_hash],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception(f"Ошибка при получении данных коммита {commit_hash}")

        files = result.stdout.splitlines()[1:]  # Скидываем строку с сообщением коммита
        return files
    except Exception as e:
        print(f"Ошибка при получении файлов для коммита {commit_hash}: {e}")
        return []

def build_dependency_graph(repo_path, file_hash):
    """Построение графа зависимостей для коммитов."""
    dependencies = []
    
    try:
        # Получаем список всех коммитов в репозитории с помощью команды git log
        result = subprocess.run(
            ["git", "log", "--pretty=format:%H"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception("Ошибка при получении списка коммитов")

        commits = result.stdout.splitlines()
        
        for commit in commits:
            files = get_commit_files(repo_path, commit)
            for file in files:
                # Проверяем, если нужный файл с хешем был изменен в коммите
                if file.endswith(file_hash):
                    dependencies.append(commit)
                    break
    except Exception as e:
        print(f"Ошибка при построении графа зависимостей: {e}")
    
    return dependencies

def generate_plantuml_code(dependencies):
    """Генерация кода для PlantUML."""
    plantuml_code = "@startuml\n"
    
    # Добавляем коммиты в граф зависимостей
    for commit in dependencies:
        plantuml_code += f"'{commit}'\n"
    
    # Визуализируем зависимости между коммитами
    for i in range(len(dependencies) - 1):
        plantuml_code += f"'{dependencies[i]}' --> '{dependencies[i + 1]}'\n"
    
    plantuml_code += "@enduml\n"
    return plantuml_code

def save_plantuml_code(plantuml_code, puml_output_path):
    """Сохраняем сгенерированный код PlantUML в файл."""
    try:
        with open(puml_output_path, "w") as puml_file:
            puml_file.write(plantuml_code)
        print(f"Граф сохранён в {puml_output_path}")
    except Exception as e:
        print(f"Ошибка при записи файла PlantUML: {e}")
        exit(1)

def generate_png_from_plantuml(plantuml_path, puml_output_path, png_output_path):
    """Генерация изображения PNG с помощью PlantUML."""
    try:
        command = ["java", "-jar", plantuml_path, puml_output_path]
        subprocess.run(command, check=True)
        print(f"PNG граф сохранён в {png_output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при генерации PNG: {e}")
        exit(1)

def main():
    # Чтение конфигурационного файла
    config_path = "config.csv"
    config = load_config(config_path)
    
    repo_path = config['repo_path']
    file_hash = config['file_hash']
    puml_output_path = config['puml_output_path']
    png_output_path = config['png_output_path']
    plantuml_path = config['plantuml_path']
    
    print(f"Конфигурация: {config}")
    print(f"Путь репозитория: {repo_path}")
    print(f"Хеш файла: {file_hash}")
    print(f"Путь для вывода PlantUML: {puml_output_path}")
    print(f"Путь для вывода PNG: {png_output_path}")
    print(f"Путь к PlantUML: {plantuml_path}")

    # Построение зависимостей для коммитов, связанных с файлом
    dependencies = build_dependency_graph(repo_path, file_hash)
    
    if not dependencies:
        print("Не найдено коммитов с заданным хешом.")
        exit(0)

    # Генерация кода PlantUML
    plantuml_code = generate_plantuml_code(dependencies)

    # Сохранение кода в файл .puml
    save_plantuml_code(plantuml_code, puml_output_path)
    
    # Генерация PNG из PlantUML
    generate_png_from_plantuml(plantuml_path, puml_output_path, png_output_path)
    
    print("Визуализация зависимостей завершена успешно.")

if __name__ == "__main__":
    main()
