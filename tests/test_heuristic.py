import unittest
from git_clarity.analyzer import DiffParser
from git_clarity.providers.heuristic import HeuristicProvider

DIFF_WITH_SECRET = """diff --git a/config.py b/config.py
new file mode 100644
--- /dev/null
+++ b/config.py
@@ -0,0 +1,2 @@
+API_KEY = "sk-1234567890abcdef"
"""


class TestHeuristicProvider(unittest.TestCase):
    def test_generate_commit(self):
        provider = HeuristicProvider()
        analysis = DiffParser.analyze(DIFF_WITH_SECRET)
        msg = provider.generate_commit_message(analysis, DIFF_WITH_SECRET)
        self.assertTrue(msg.startswith("feat(config):"))
        self.assertIn("config.py", msg)

    def test_security_detection(self):
        provider = HeuristicProvider()
        analysis = DiffParser.analyze(DIFF_WITH_SECRET)
        reviews = provider.review_changes(analysis, DIFF_WITH_SECRET)
        levels = [r["level"] for r in reviews]
        self.assertIn("CRITICAL", levels)


if __name__ == "__main__":
    unittest.main()
