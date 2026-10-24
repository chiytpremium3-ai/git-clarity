import os
import json
from typing import List, Dict, Any, Optional
from git_clarity.providers.base import BaseProvider
from git_clarity.analyzer import DiffAnalysis
from git_clarity.providers.heuristic import HeuristicProvider


class OpenAIProvider(BaseProvider):
    """
    OpenAI-backed provider using models like gpt-4o or o1-mini for semantic
    commit generation and comprehensive security/logic reviews.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self._fallback = HeuristicProvider()

    def _get_client(self):
        if not self.api_key:
            return None
        try:
            from openai import OpenAI
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            return OpenAI(**kwargs)
        except ImportError:
            return None

    def generate_commit_message(self, analysis: DiffAnalysis, raw_diff: str) -> str:
        client = self._get_client()
        if not client:
            return self._fallback.generate_commit_message(analysis, raw_diff)

        prompt = (
            "You are an expert developer assistant following Conventional Commits v1.0.0.\n"
            "Given the git diff below, output ONLY the conventional commit message (Type(scope): subject).\n"
            "Followed by a concise bullet list explaining changes.\n\n"
            f"Git Diff Summary: {analysis.summary}\n"
            f"Diff Content:\n{raw_diff[:4000]}"
        )

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You output only clean, production-ready conventional commits."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return self._fallback.generate_commit_message(analysis, raw_diff)

    def review_changes(self, analysis: DiffAnalysis, raw_diff: str) -> List[Dict[str, Any]]:
        client = self._get_client()
        if not client:
            return self._fallback.review_changes(analysis, raw_diff)

        prompt = (
            "Analyze this git diff for code quality, architectural consistency, edge cases, and security vulnerabilities.\n"
            "Return a JSON array of objects with keys: 'file', 'level' (CRITICAL/WARNING/INFO/PASS), 'category', 'message'.\n"
            f"Diff:\n{raw_diff[:4000]}"
        )

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior tech lead and security auditor. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"} if "4o" in self.model else None
            )
            content = response.choices[0].message.content.strip()
            data = json.loads(content)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                for val in data.values():
                    if isinstance(val, list):
                        return val
            return self._fallback.review_changes(analysis, raw_diff)
        except Exception:
            return self._fallback.review_changes(analysis, raw_diff)
