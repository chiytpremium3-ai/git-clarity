import subprocess
import os
from typing import List, Dict, Optional, Tuple


class GitError(Exception):
    """Base exception for Git operations."""
    pass


class GitRepo:
    def __init__(self, path: Optional[str] = None):
        self.path = os.path.abspath(path or os.getcwd())
        if not self.is_git_repo():
            raise GitError(f"Directory is not a valid Git repository: {self.path}")

    def _run(self, args: List[str]) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitError(f"Git command failed: {' '.join(args)}\nError: {e.stderr.strip()}")

    def is_git_repo(self) -> bool:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.path,
                capture_output=True,
                text=True
            )
            return res.returncode == 0 and res.stdout.strip() == "true"
        except Exception:
            return False

    def get_staged_diff(self) -> str:
        """Returns the diff of staged changes."""
        return self._run(["diff", "--cached"])

    def get_unstaged_diff(self) -> str:
        """Returns the diff of unstaged changes."""
        return self._run(["diff"])

    def get_staged_files(self) -> List[str]:
        """Returns list of staged files."""
        output = self._run(["diff", "--cached", "--name-only"])
        return [f for f in output.splitlines() if f]

    def get_status_summary(self) -> Dict[str, List[str]]:
        """Returns status of staged and untracked files."""
        output = self._run(["status", "--porcelain"])
        staged = []
        unstaged = []
        untracked = []

        for line in output.splitlines():
            if len(line) < 3:
                continue
            index_status = line[0]
            work_tree_status = line[1]
            file_path = line[3:].strip()

            if index_status in ["M", "A", "D", "R", "C"]:
                staged.append(file_path)
            if work_tree_status in ["M", "D"]:
                unstaged.append(file_path)
            elif index_status == "?" and work_tree_status == "?":
                untracked.append(file_path)

        return {
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked
        }

    def commit(self, message: str) -> str:
        """Executes a git commit with the given message."""
        return self._run(["commit", "-m", message])

    def get_recent_commits(self, count: int = 10) -> List[Dict[str, str]]:
        """Returns recent commits with hash, author, date, and subject."""
        format_str = "%H%x1f%an%x1f%ad%x1f%s"
        output = self._run(["log", f"-n{count}", f"--pretty=format:{format_str}", "--date=short"])
        commits = []
        for line in output.splitlines():
            if not line:
                continue
            parts = line.split("\x1f")
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "subject": parts[3]
                })
        return commits

    def get_current_branch(self) -> str:
        """Returns current branch name."""
        return self._run(["rev-parse", "--abbrev-ref", "HEAD"])
