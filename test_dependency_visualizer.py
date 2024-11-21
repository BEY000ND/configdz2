import os
import subprocess  # Импортируем subprocess для использования в тестах
import unittest
from unittest.mock import patch, MagicMock
from dependency_visualizer import run_command, get_changed_files, generate_puml, generate_png

class TestDependencyVisualizer(unittest.TestCase):

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run):
        # Настроим мок для успешного выполнения команды
        mock_run.return_value = MagicMock(stdout="Success", stderr="", returncode=0)
        command = ["echo", "Success"]
        result = run_command(command)
        self.assertEqual(result, "Success")
        mock_run.assert_called_once_with(command, cwd=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        # Настроим мок для ошибки выполнения команды
        mock_run.return_value = MagicMock(stdout="", stderr="Error occurred", returncode=1)
        command = ["some", "failing", "command"]
        with self.assertRaises(Exception) as context:
            run_command(command)
        self.assertIn("Error running command", str(context.exception))

    @patch("os.makedirs")
    @patch("builtins.open", create=True)
    def test_generate_puml(self, mock_open, mock_makedirs):
        changed_files = ["file1.py", "file2.py"]
        puml_output_path = r"C:\Users\panze\OneDrive\Документы\vuz\config\dz2\output\graph.puml"

        generate_puml(changed_files, puml_output_path)

        # Проверяем, что директория создана
        mock_makedirs.assert_called_once_with(os.path.dirname(puml_output_path), exist_ok=True)

        # Проверяем, что файл открыт для записи
        mock_open.assert_called_once_with(puml_output_path, 'w', encoding='utf-8')

    @patch("dependency_visualizer.run_command")
    def test_generate_png(self, mock_run_command):
        plantuml_path = r"C:/path/to/plantuml.jar"
        puml_path = r"C:/path/to/output/graph.puml"
        png_output_path = r"C:/path/to/output/graph.png"

        generate_png(puml_path, png_output_path, plantuml_path)

        # Проверяем, что run_command был вызван с правильными аргументами
        mock_run_command.assert_called_once_with(
            ["java", "-jar", plantuml_path, puml_path, "-o", os.path.dirname(png_output_path)]
        )

    @patch("dependency_visualizer.run_command")
    def test_get_changed_files(self, mock_run_command):
        mock_run_command.return_value = "file1.py\nfile2.py\n"
        repo_path = r"C:/path/to/repo"
        commit_hash = "123abc"

        result = get_changed_files(commit_hash, repo_path)

        # Проверяем результат
        self.assertEqual(result, ["file1.py", "file2.py"])

        # Проверяем, что run_command был вызван правильно
        mock_run_command.assert_called_once_with(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
            cwd=repo_path
        )

if __name__ == "__main__":
    unittest.main()
