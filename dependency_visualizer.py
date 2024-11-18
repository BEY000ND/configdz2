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
    command = ["git", "-C", repo_path, "log", "--pretty=format:%H %s"]
    result = subprocess.run(command, capture_output=True, text=True)
    commits = result.stdout.splitlines()

    relevant_commits = []
    for commit in commits:
        commit_hash, commit_message = commit.split(" ", 1)
        command = ["git", "-C", repo_path, "show", "--name-only", "--pretty=format:", commit_hash]
        result = subprocess.run(command, capture_output=True, text=True)
        changed_files = result.stdout.splitlines()
        for file in changed_files:
            if file_hash in file:
                relevant_commits.append((commit_hash, commit_message))
                break
    return relevant_commits

def generate_plantuml_graph(commits, puml_output_path, png_output_path, plantuml_path):
    """
    Генерация графа зависимостей и сохранение в формате PNG.
    :param commits: Список коммитов
    :param puml_output_path: Путь для сохранения PlantUML файла
    :param png_output_path: Путь для сохранения PNG файла
    :param plantuml_path: Путь к PlantUML jar
    """
    plantuml_code = "@startuml\n"
    for i, commit in enumerate(commits):
        commit_hash, commit_message = commit
        plantuml_code += f"'{commit_hash[:7]}' : {commit_message.replace('\n', ' ')}\n"
        if i > 0:
            prev_commit_hash = commits[i - 1][0]
            plantuml_code += f"'{prev_commit_hash[:7]}' --> '{commit_hash[:7]}'\n"
    plantuml_code += "@enduml"

    with open(puml_output_path, "w", encoding="utf-8") as f:
        f.write(plantuml_code)

    # Вызываем plantuml.jar для создания PNG
    subprocess.run(["java", "-jar", plantuml_path, puml_output_path, "-o", os.path.dirname(png_output_path)])

def main():
    # Загружаем конфигурацию из CSV
    with open("config.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        config = {row[0]: row[1] for row in reader}

    repo_path = config["repo_path"]
    file_hash = config["file_hash"]
    puml_output_path = config["puml_output_path"]
    png_output_path = config["png_output_path"]
    plantuml_path = config["plantuml_path"]

    # Получаем коммиты с зависимостями
    commits = get_commit_dependencies(repo_path, file_hash)
    if commits:
        generate_plantuml_graph(commits, puml_output_path, png_output_path, plantuml_path)
        print(f"Граф зависимостей успешно создан и сохранен в {png_output_path}")
    else:
        print("Не найдено зависимостей для данного файла.")

if __name__ == "__main__":
    main()
