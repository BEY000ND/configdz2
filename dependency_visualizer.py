import subprocess
import os
import csv

def get_commit_dependencies(repo_path, file_hash):
    """
    Получаем все коммиты, где упоминается файл с заданным хешем.
    :param repo_path: Путь к репозиторию
    :param file_hash: Хеш файла для поиска зависимостей
    :return: Список коммитов, содержащих зависимости
    """
    # Получаем список всех коммитов с их хешами и сообщениями
    command = ["git", "-C", repo_path, "log", "--pretty=format:%H %s"]
    result = subprocess.run(command, capture_output=True, text=True)

    # Разбираем результаты
    commits = result.stdout.splitlines()

    relevant_commits = []  # Список коммитов, в которых упоминается файл с нужным хешем

    # Проверяем каждый коммит на наличие изменений в нужном файле
    for commit in commits:
        commit_hash, commit_message = commit.split(" ", 1)

        # Отладочный вывод: показываем коммит и его сообщение
        print(f"Checking commit {commit_hash} with message: {commit_message}")

        # Получаем список измененных файлов в этом коммите
        command = ["git", "-C", repo_path, "show", "--name-only", "--pretty=format:", commit_hash]
        result = subprocess.run(command, capture_output=True, text=True)
        changed_files = result.stdout.splitlines()

        # Отладочный вывод: показываем измененные файлы в коммите
        print(f"Changed files in commit {commit_hash}: {changed_files}")

        # Проверяем, есть ли среди измененных файлов наш файл с нужным хешем
        for file in changed_files:
            if file_hash in file:
                relevant_commits.append((commit_hash, commit_message))
                break  # Прерываем, если нашли нужный файл

    return relevant_commits

def generate_plantuml_graph(commits, output_path):
    """
    Генерируем код PlantUML для визуализации графа зависимостей.
    :param commits: Список коммитов
    :param output_path: Путь для сохранения изображения
    """
    plantuml_code = "@startuml\n"  # Начало кода PlantUML

    # Добавляем коммиты в граф
    for commit in commits:
        commit_hash, commit_message = commit
        plantuml_code += f"'{commit_hash[:7]}' : {commit_message.replace('\n', ' ')}\n"
        if len(commits) > 1:
            # Добавляем зависимость между коммитами
            plantuml_code += f"'{commit_hash[:7]}' --> '{commits[commits.index(commit)+1][0][:7]}'\n"

    plantuml_code += "@enduml"  # Конец кода PlantUML

    # Сохраняем код PlantUML в файл
    with open("dependency.puml", "w") as f:
        f.write(plantuml_code)

    # Генерация PNG с помощью PlantUML (с помощью Java)
    subprocess.run(["java", "-jar", "C:\\path\\to\\plantuml.jar", "dependency.puml"])

    # Переименовываем и сохраняем изображение в нужную папку
    os.rename("dependency.png", output_path)
    os.remove("dependency.puml")  # Удаляем файл PlantUML после генерации изображения

def main():
    # Загружаем конфигурацию из CSV
    with open("config.csv", "r") as f:
        reader = csv.reader(f)
        config = {row[0]: row[1] for row in reader}

    # Получаем параметры из конфигурации
    repo_path = config["repo_path"]
    output_path = config["puml_output_path"]
    file_hash = config["file_hash"]

    # Получаем коммиты с зависимостями
    commits = get_commit_dependencies(repo_path, file_hash)

    if commits:
        # Генерация и сохранение графа зависимостей
        generate_plantuml_graph(commits, output_path)
        print(f"Граф зависимостей успешно создан и сохранен в {output_path}")
    else:
        print("Не найдено зависимостей для данного файла.")

if __name__ == "__main__":
    main()
