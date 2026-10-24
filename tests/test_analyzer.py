import unittest
from git_clarity.analyzer import DiffParser, FileDiff


SAMPLE_DIFF = """diff --git a/git_clarity/cli.py b/git_clarity/cli.py
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/git_clarity/cli.py
@@ -0,0 +1,15 @@
+def main():
+    print("Hello world")
+
+class Runner:
+    pass
diff --git a/README.md b/README.md
index 1111111..2222222 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
-# Project
+# Git Clarity
+Awesome tool
"""


class TestDiffParser(unittest.TestCase):
    def test_parse_diff_files(self):
        files = DiffParser.parse(SAMPLE_DIFF)
        self.assertEqual(len(files), 2)

        cli_diff = files[0]
        self.assertEqual(cli_diff.filename, "git_clarity/cli.py")
        self.assertTrue(cli_diff.is_new)
        self.assertEqual(cli_diff.additions, 5)
        self.assertIn("main", cli_diff.modified_symbols)
        self.assertIn("Runner", cli_diff.modified_symbols)

        readme_diff = files[1]
        self.assertEqual(readme_diff.filename, "README.md")
        self.assertFalse(readme_diff.is_new)
        self.assertEqual(readme_diff.deletions, 1)
        self.assertEqual(readme_diff.additions, 2)

    def test_empty_diff(self):
        files = DiffParser.parse("")
        self.assertEqual(files, [])

    def test_analyze_summary(self):
        analysis = DiffParser.analyze(SAMPLE_DIFF)
        self.assertEqual(analysis.total_additions, 7)
        self.assertEqual(analysis.total_deletions, 1)
        self.assertEqual(analysis.suggested_type, "feat")
        self.assertIn("git_clarity", analysis.primary_scope)


if __name__ == "__main__":
    unittest.main()
