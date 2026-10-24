import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class FileDiff:
    old_path: str
    new_path: str
    is_new: bool = False
    is_deleted: bool = False
    additions: int = 0
    deletions: int = 0
    hunks: List[str] = field(default_factory=list)
    modified_symbols: List[str] = field(default_factory=list)

    @property
    def filename(self) -> str:
        return self.new_path if not self.is_deleted else self.old_path

    @property
    def extension(self) -> str:
        parts = self.filename.split(".")
        return parts[-1] if len(parts) > 1 else ""


@dataclass
class DiffAnalysis:
    files: List[FileDiff]
    total_additions: int = 0
    total_deletions: int = 0
    primary_scope: str = ""
    suggested_type: str = "chore"
    summary: str = ""

    @property
    def total_changes(self) -> int:
        return self.total_additions + self.total_deletions


class DiffParser:
    """Parses raw unified git diffs into structured FileDiff models."""

    @staticmethod
    def parse(raw_diff: str) -> List[FileDiff]:
        if not raw_diff or not raw_diff.strip():
            return []

        file_diffs: List[FileDiff] = []
        current_file: Optional[FileDiff] = None
        current_hunk: List[str] = []

        lines = raw_diff.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]

            # Detect file boundaries
            if line.startswith("diff --git "):
                if current_file:
                    if current_hunk:
                        current_file.hunks.append("\n".join(current_hunk))
                    file_diffs.append(current_file)

                # Parse paths: diff --git a/path b/path
                match = re.match(r"diff --git a/(.*) b/(.*)", line)
                if match:
                    old_path, new_path = match.group(1), match.group(2)
                else:
                    parts = line.split(" ")
                    old_path = parts[2][2:] if len(parts) > 2 else ""
                    new_path = parts[3][2:] if len(parts) > 3 else ""

                current_file = FileDiff(old_path=old_path, new_path=new_path)
                current_hunk = []
                i += 1
                continue

            if not current_file:
                i += 1
                continue

            # Detect new/deleted files
            if line.startswith("new file mode"):
                current_file.is_new = True
            elif line.startswith("deleted file mode"):
                current_file.is_deleted = True
            elif line.startswith("@@"):
                # Hunk header @@ -1,5 +1,6 @@ optional function context
                if current_hunk:
                    current_file.hunks.append("\n".join(current_hunk))
                    current_hunk = []
                # Check symbol context in hunk header
                match = re.search(r"@@\s*(def|class|function|fn|async def)\s+([a-zA-Z0-9_]+)", line)
                if match:
                    current_file.modified_symbols.append(match.group(2))
                current_hunk.append(line)
            elif line.startswith("+") and not line.startswith("+++"):
                current_file.additions += 1
                current_hunk.append(line)
                # Quick symbol detection in added lines
                sym_match = re.search(r"^\+\s*(?:def|class|function|async def)\s+([a-zA-Z0-9_]+)", line)
                if sym_match and sym_match.group(1) not in current_file.modified_symbols:
                    current_file.modified_symbols.append(sym_match.group(1))
            elif line.startswith("-") and not line.startswith("---"):
                current_file.deletions += 1
                current_hunk.append(line)
            else:
                current_hunk.append(line)

            i += 1

        if current_file:
            if current_hunk:
                current_file.hunks.append("\n".join(current_hunk))
            file_diffs.append(current_file)

        return file_diffs

    @classmethod
    def analyze(cls, raw_diff: str) -> DiffAnalysis:
        files = cls.parse(raw_diff)
        total_add = sum(f.additions for f in files)
        total_del = sum(f.deletions for f in files)

        # Determine primary scope
        scopes = {}
        for f in files:
            parts = f.filename.split("/")
            if len(parts) > 1:
                scope = parts[0] if parts[0] not in ["src", "lib"] else (parts[1] if len(parts) > 2 else parts[0])
            else:
                scope = f.filename.split(".")[0]
            scopes[scope] = scopes.get(scope, 0) + (f.additions + f.deletions + 1)

        primary_scope = max(scopes, key=scopes.get) if scopes else "core"

        # Determine suggested type based on heuristic rules
        suggested_type = cls._infer_type(files)

        return DiffAnalysis(
            files=files,
            total_additions=total_add,
            total_deletions=total_del,
            primary_scope=primary_scope,
            suggested_type=suggested_type,
            summary=f"Changed {len(files)} files with +{total_add} -{total_del} lines."
        )

    @staticmethod
    def _infer_type(files: List[FileDiff]) -> str:
        filenames = [f.filename.lower() for f in files]

        if all(any(ext in fn for ext in ["test", "spec", "_test.py", ".test.ts"]) for fn in filenames):
            return "test"
        if all(any(ext in fn for ext in [".md", "doc", "docs", "readme", "license"]) for fn in filenames):
            return "docs"
        if all(any(ext in fn for ext in [".github", "docker", "compose", "makefile", "ci.yml"]) for fn in filenames):
            return "ci"
        if all(any(ext in fn for ext in ["package.json", "pyproject.toml", "cargo.toml", "requirements.txt"]) for fn in filenames):
            return "build"

        # If additions significantly outnumber deletions or new files are introduced
        if any(f.is_new for f in files) or any("add" in s.lower() or "new" in s.lower() for f in files for s in f.modified_symbols):
            return "feat"

        # Check for bugfix patterns in filenames or diffs
        for f in files:
            for hunk in f.hunks:
                if any(k in hunk.lower() for k in ["fix", "error", "bug", "prevent", "patch"]):
                    return "fix"

        return "feat" if sum(f.additions for f in files) > 20 else "refactor"
