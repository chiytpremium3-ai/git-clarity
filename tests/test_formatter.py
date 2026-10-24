import unittest
from git_clarity.formatter import MarkdownFormatter


class TestFormatter(unittest.TestCase):
    def test_format_review_report(self):
        reviews = [
            {"file": "auth.py", "level": "CRITICAL", "category": "Security", "message": "Secret leak found"},
            {"file": "cli.py", "level": "PASS", "category": "Quality", "message": "Clean structure"}
        ]
        md = MarkdownFormatter.format_review_report(reviews)
        self.assertIn("Git Clarity Code Review Report", md)
        self.assertIn("CRITICAL", md)
        self.assertIn("auth.py", md)

    def test_format_changelog(self):
        commits = [
            {"hash": "abcdef123456", "subject": "feat(core): add parser engine"},
            {"hash": "123456abcdef", "subject": "fix(cli): resolve flag parsing bug"},
            {"hash": "7890abcdef12", "subject": "docs: update install guide"}
        ]
        cl = MarkdownFormatter.format_changelog(commits)
        self.assertIn("Release Changelog", cl)
        self.assertIn("Features", cl)
        self.assertIn("Bug Fixes", cl)
        self.assertIn("Documentation", cl)
        self.assertIn("abcdef1", cl)


if __name__ == "__main__":
    unittest.main()
