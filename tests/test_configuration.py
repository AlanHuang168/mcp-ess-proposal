import ast
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return (PROJECT_ROOT / path).read_text()


class ConfigurationContractTests(unittest.TestCase):
    def test_env_example_declares_no_variables(self):
        lines = text(".env.example").splitlines()

        assignments = [
            line for line in lines if line.strip() and not line.lstrip().startswith("#")
        ]
        self.assertEqual(assignments, [])

    def test_runtime_source_does_not_read_environment_configuration(self):
        source_files = sorted((PROJECT_ROOT / "src" / "mcp_ess_proposal").glob("*.py"))

        for source_file in source_files:
            tree = ast.parse(source_file.read_text(), filename=str(source_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertNotIn("os", [alias.name for alias in node.names])
                if isinstance(node, ast.ImportFrom):
                    self.assertNotEqual(node.module, "os")

    def test_core_config_docs_do_not_declare_old_private_settings(self):
        forbidden_names = [
            "HGP_" + "DATA" + "BASE_URL",
            "DATA" + "BASE_URL",
            "DEEP" + "SEEK_API_KEY",
            "DASH" + "SCOPE_API_KEY",
        ]
        checked_paths = [
            ".env.example",
            "README.md",
            "pyproject.toml",
        ]

        for path in checked_paths:
            content = text(path)
            for forbidden_name in forbidden_names:
                self.assertNotIn(forbidden_name, content)

    def test_gitignore_keeps_real_env_files_untracked(self):
        content = text(".gitignore")

        self.assertRegex(content, re.compile(r"^\.env$", re.MULTILINE))
        self.assertRegex(content, re.compile(r"^\.env\.\*$", re.MULTILINE))
        self.assertRegex(content, re.compile(r"^!\.env\.example$", re.MULTILINE))


if __name__ == "__main__":
    unittest.main()
