import unittest
from unittest.mock import patch, MagicMock
import subprocess

class TestDependencyVisualizer(unittest.TestCase):

    @patch("subprocess.run")
    def test_get_commit_dependencies(self, mock_run):
        # Мокируем subprocess.run для возврата фиксированных данных
        mock_run.return_value.stdout = "commit_hash1 Commit message 1\ncommit_hash2 Commit message 2"
        
        # Настройка теста
        repo_path = "C:\\path\\to\\repo"
        file_hash = "d35b0d1c0f6f6d1c0510841cc63d7db26e55c8f0"
        
        # Вызов тестируемой функции
        commits = get_commit_dependencies(repo_path, file_hash)
        
        # Проверка результата
        self.assertEqual(len(commits), 2)

    @patch("subprocess.run")
    def test_generate_plantuml_graph(self, mock_run):
        # Мокируем subprocess.run
        mock_run.return_value = MagicMock()
        
        # Пример коммитов
        commits = [("commit_hash1", "Commit message 1"), ("commit_hash2", "Commit message 2")]
        output_path = "C:\\path\\to\\output\\dependency_graph.png"
        
        # Вызов тестируемой функции
        generate_plantuml_graph(commits, output_path)
        
        # Проверка вызова subprocess для создания PNG
        mock_run.assert_called_with(["java", "-jar", "C:\\path\\to\\plantuml.jar", "dependency.puml"])

if __name__ == "__main__":
    unittest.main()
