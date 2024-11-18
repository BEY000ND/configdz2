import subprocess
import os
import csv

def get_commit_dependencies(repo_path, file_hash):
    """
    Получает список коммитов, в которых был изменен файл с заданным хешем.
    :param repo_path: Путь к локальному репозиторию Git
    :param file_hash: Хеш файла для поиска зависимостей
    :return: Список коммитов, которые содержат зависимость
    """
    # Команда для получения всех коммитов с их хешами и сообщениями
    command = ["git", "-C", repo_path, "log", "--pretty=format:%H %s"]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='ignore')  # Указана кодировка UTF-8 с игнорированием ошибок
    
    # Получаем все коммиты
    commits = result.stdout.splitlines()
    
    relevant_commits = []  # Список коммитов, где упоминается файл с данным хешем
    for commit in commits:
        commit_hash, commit_message = commit.split(" ", 1)
        
        # Команда для получения изменений в файле в каждом коммите
        command = ["git", "-C", repo_path, "show", "--name-only", "--pretty=format:", commit_hash]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='ignore')  # Указана кодировка UTF-8 с игнорированием ошибок
        
        changed_files = result.stdout.splitlines()
        
        for file in changed_files:
            if file_hash in file:
                relevant_commits.append((commit_hash, commit_message))
                break
    
    return relevant_commits

def generate_plantuml_graph(commits, output_path):
    """
    Генерирует код PlantUML для визуализации графа зависимостей.
    :param commits: Список коммитов
    :param output_path: Путь для сохранения изображения
    """
    plantuml_code = "@startuml\n"  # Начало кода PlantUML
    
    for commit in commits:
        commit_hash, commit_message = commit
        plantuml_code += f"'{commit_hash[:7]}' : {commit_message.replace('\n', ' ')}\n"
        if len(commits) > 1:
            # Добавляем зависимость между коммитами
            plantuml_code += f"'{commit_hash[:7]}' --> '{commits[commits.index(commit)+1][0][:7]}'\n"
    
    plantuml_code += "@enduml"  # Конец кода PlantUML
    
    # Сохраняем код PlantUML в файл
    with open("dependency.puml", "w", encoding='utf-8') as f:  # Указана кодировка UTF-8
        f.write(plantuml_code)
    
    # Генерация PNG с помощью PlantUML (с помощью Java)
    subprocess.run(["java", "-jar", "C:\\path\\to\\plantuml.jar", "dependency.puml"], encoding='utf-8', errors='ignore')
    
    # Переименовываем и сохраняем изображение в нужную папку
    os.rename("dependency.png", output_path)
    os.remove("dependency.puml")  # Удаляем файл PlantUML после генерации изображения

def main():
    # Загружаем конфигурацию из CSV
    with open("config.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        config = {row[0]: row[1] for row in reader}
    
    # Выводим содержимое config для проверки
    print("Конфигурация:", config)

    # Проверяем наличие всех необходимых параметров
    if "repo_path" not in config or "file_hash" not in config or "puml_output_path" not in config or "png_output_path" not in config or "plantuml_path" not in config:
        print("Ошибка: Параметры конфигурации отсутствуют!")
        return
    
    repo_path = config["repo_path"]
    file_hash = config["file_hash"]
    puml_output_path = config["puml_output_path"]
    png_output_path = config["png_output_path"]
    plantuml_path = config["plantuml_path"]

    # Получаем коммиты с зависимостями
    commits = get_commit_dependencies(repo_path, file_hash)
    
    if commits:
        generate_plantuml_graph(commits, puml_output_path)
        generate_png_from_puml(puml_output_path, png_output_path, plantuml_path)
        print(f"Граф зависимостей успешно создан и сохранен в {png_output_path}")
    else:
        print("Не найдено зависимостей для данного файла.")
        
if __name__ == "__main__":
    main()
