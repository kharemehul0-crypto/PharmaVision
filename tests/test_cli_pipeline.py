"""
End-to-end CLI integration test.
"""

import unittest
import subprocess
import sys
import os


class TestCLIPipeline(unittest.TestCase):

    def setUp(self):
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.main_script = os.path.join(self.project_root, "main.py")

    def test_cli_help(self):
        result = subprocess.run(
            [sys.executable, self.main_script, "--help"],
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("PharmaCount-CV", result.stdout)

    def test_cli_generate_and_benchmark(self):
        # Test benchmark execution
        result = subprocess.run(
            [sys.executable, self.main_script, "--benchmark"],
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("BENCHMARK EVALUATION", result.stdout)
        self.assertIn("Acc", result.stdout)


if __name__ == "__main__":
    unittest.main()
