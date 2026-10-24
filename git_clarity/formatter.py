from typing import List, Dict, Any


class MarkdownFormatter:
    """Formats review results and changelog entries into clean GitHub Markdown."""

    @staticmethod
    def format_review_report(reviews: List[Dict[str, Any]]) -> str:
        lines = [
            "### 🔍 Git Clarity Code Review Report",
            "",
            "| Level | File | Category | Findings |",
            "| :--- | :--- | :--- | :--- |"
        ]

        icons = {
            "CRITICAL": "🚨 `CRITICAL`",
            "WARNING": "⚠️ `WARNING`",
            "INFO": "ℹ️ `INFO`",
            "PASS": "✅ `PASS`"
        }

        for r in reviews:
            lvl = icons.get(r.get("level", "INFO"), r.get("level", "INFO"))
            f = f"`{r.get('file', 'N/A')}`"
            cat = r.get("category", "General")
            msg = r.get("message", "").replace("|", "\\|")
            lines.append(f"| {lvl} | {f} | {cat} | {msg} |")

        lines.append("")
        lines.append("> _Generated automatically by [Git Clarity](https://github.com)_")
        return "\n".join(lines)

    @staticmethod
    def format_changelog(commits: List[Dict[str, str]]) -> str:
        categories = {
            "Features": [],
            "Bug Fixes": [],
            "Refactoring & Maintenance": [],
            "Documentation": [],
            "Other": []
        }

        for c in commits:
            subj = c.get("subject", "")
            h = c.get("hash", "")[:7]
            entry = f"- {subj} (`{h}`)"

            lower = subj.lower()
            if lower.startswith("feat"):
                categories["Features"].append(entry)
            elif lower.startswith("fix"):
                categories["Bug Fixes"].append(entry)
            elif lower.startswith("refactor") or lower.startswith("chore") or lower.startswith("perf"):
                categories["Refactoring & Maintenance"].append(entry)
            elif lower.startswith("docs"):
                categories["Documentation"].append(entry)
            else:
                categories["Other"].append(entry)

        output = ["## 📦 Release Changelog", ""]
        for cat, items in categories.items():
            if items:
                output.append(f"### {cat}")
                output.extend(items)
                output.append("")

        return "\n".join(output)
