import os
import subprocess
import csv

# Функция для выполнения команд
def run_command(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Error running command {' '.join(command)}: {result.stderr}")
    return result.stdout

# Функция для извлечения списка измененных файлов из коммита
def get_changed_files(commit_hash, repo_path):
    command = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash]
    result = run_command(command, cwd=repo_path)
    return result.splitlines()

# Функция для создания диаграммы .puml
def generate_puml(changed_files, puml_output_path):
    os.makedirs(os.path.dirname(puml_output_path), exist_ok=True)
    with open(puml_output_path, 'w', encoding='utf-8') as f:
        f.write('@startuml\n')
        for file in changed_files:
            f.write(f'[{file}] --> [{file}_dependency]\n')  # Условная зависимость
        f.write('@enduml\n')

# Функция для генерации PNG из PlantUML
def generate_png(puml_path, png_output_path, plantuml_path):
    command = ["java", "-jar", plantuml_path, puml_path, "-o", os.path.dirname(png_output_path)]
    run_command(command)
    print(f"PNG файл сгенерирован: {png_output_path}")

# Основная функция
def main():
    # Загрузка конфигурации из CSV
    config = {}
    with open('config.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            config = row

    # Параметры конфигурации
    repo_path = config['repo_path']
    file_hash = config['file_hash']
    puml_output_path = config['puml_output_path']
    png_output_path = config['png_output_path']
    plantuml_path = config['plantuml_path']

    # Получаем измененные файлы для указанного хеша
    print(f"Получаем измененные файлы для коммита {file_hash}...")
    changed_files = get_changed_files(file_hash, repo_path)

    if not changed_files:
        print("Нет изменений в файлах для этого коммита.")
        return

    print("Измененные файлы:", changed_files)

    # Генерируем файл .puml
    print(f"Создание диаграммы .puml в {puml_output_path}...")
    generate_puml(changed_files, puml_output_path)
    print(f"Файл {puml_output_path} успешно создан.")

    # Генерируем файл .png
    print(f"Создание диаграммы .png в {png_output_path}...")
    generate_png(puml_output_path, png_output_path, plantuml_path)

if __name__ == "__main__":
    main()
