from abc import ABC, abstractmethod
from typing import Dict, Any, List
from git_clarity.analyzer import DiffAnalysis


class BaseProvider(ABC):
    """Abstract base class for commit generation and review providers."""

    @abstractmethod
    def generate_commit_message(self, analysis: DiffAnalysis, raw_diff: str) -> str:
        """Generates a conventional commit message."""
        pass

    @abstractmethod
    def review_changes(self, analysis: DiffAnalysis, raw_diff: str) -> List[Dict[str, Any]]:
        """Returns structured review feedback on code quality, security, and edge cases."""
        pass
