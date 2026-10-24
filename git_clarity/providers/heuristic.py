from typing import List, Dict, Any
from git_clarity.providers.base import BaseProvider
from git_clarity.analyzer import DiffAnalysis


class HeuristicProvider(BaseProvider):
    """
    Offline heuristic provider that generates clean conventional commits
    and performs static rule checks without requiring external LLM API keys.
    """

    def generate_commit_message(self, analysis: DiffAnalysis, raw_diff: str) -> str:
        commit_type = analysis.suggested_type
        scope = analysis.primary_scope

        # Build concise subject
        if len(analysis.files) == 1:
            file = analysis.files[0]
            if file.is_new:
                desc = f"create {file.filename}"
            elif file.is_deleted:
                desc = f"remove {file.filename}"
            elif file.modified_symbols:
                desc = f"update {', '.join(file.modified_symbols[:2])}"
            else:
                desc = f"update {file.filename}"
        else:
            if commit_type == "test":
                desc = "add and update unit test suites"
            elif commit_type == "docs":
                desc = "update project documentation and guides"
            elif commit_type == "fix":
                desc = "resolve identified runtime edge cases"
            elif commit_type == "feat":
                desc = f"implement new capabilities across {len(analysis.files)} modules"
            else:
                desc = f"refactor {len(analysis.files)} files for cleaner structure"

        subject = f"{commit_type}({scope}): {desc}"

        # Build body bullets
        body_lines = []
        for f in analysis.files[:5]:
            status = "add" if f.is_new else ("delete" if f.is_deleted else "update")
            syms = f" ({', '.join(f.modified_symbols[:2])})" if f.modified_symbols else ""
            body_lines.append(f"- {status} `{f.filename}`{syms}: +{f.additions}/-{f.deletions}")

        if len(analysis.files) > 5:
            body_lines.append(f"- ... and {len(analysis.files) - 5} additional files")

        return f"{subject}\n\n" + "\n".join(body_lines)

    def review_changes(self, analysis: DiffAnalysis, raw_diff: str) -> List[Dict[str, Any]]:
        reviews = []

        # Rule 1: Check for hardcoded secrets or API tokens
        for f in analysis.files:
            for hunk in f.hunks:
                for line in hunk.splitlines():
                    if line.startswith("+"):
                        lower = line.lower()
                        if any(k in lower for k in ["api_key =", "secret =", "password =", "bearer "]):
                            reviews.append({
                                "file": f.filename,
                                "level": "CRITICAL",
                                "category": "Security",
                                "message": "Potential hardcoded secret or token detected in addition."
                            })
                            break

        # Rule 2: Check for test coverage
        has_src_changes = any(f.extension in ["py", "js", "ts", "go", "rs"] and "test" not in f.filename for f in analysis.files)
        has_test_changes = any("test" in f.filename for f in analysis.files)
        if has_src_changes and not has_test_changes:
            reviews.append({
                "file": "General",
                "level": "WARNING",
                "category": "Testing",
                "message": "Source code modified without corresponding unit test updates."
            })

        # Rule 3: Check for large deletions without explanation
        for f in analysis.files:
            if f.deletions > 50 and f.additions < 10:
                reviews.append({
                    "file": f.filename,
                    "level": "INFO",
                    "category": "Maintainability",
                    "message": f"Large code reduction (-{f.deletions} lines). Ensure dependent imports are not broken."
                })

        # Rule 4: Clean passes
        if not reviews:
            reviews.append({
                "file": "General",
                "level": "PASS",
                "category": "Quality",
                "message": f"Diff looks clean and well-scoped across {len(analysis.files)} files."
            })

        return reviews
