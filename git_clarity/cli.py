import sys
import os
import argparse
from git_clarity.git_utils import GitRepo, GitError
from git_clarity.analyzer import DiffParser
from git_clarity.providers.openai_provider import OpenAIProvider
from git_clarity.providers.heuristic import HeuristicProvider
from git_clarity.formatter import MarkdownFormatter


# ANSI terminal styling helper
class Style:
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner():
    banner = f"{Style.CYAN}{Style.BOLD}⚡ Git Clarity v0.2.1{Style.RESET} {Style.DIM}— AI-Native Git Workflow & Review Assistant{Style.RESET}"
    print(banner)
    print("-" * 60)


def get_provider(use_ai: bool = True):
    if use_ai and os.getenv("OPENAI_API_KEY"):
        return OpenAIProvider()
    return HeuristicProvider()


def cmd_commit(args):
    repo = GitRepo()
    staged_diff = repo.get_staged_diff()

    if not staged_diff.strip():
        print(f"{Style.YELLOW}⚠️  No staged changes found.{Style.RESET}")
        print("Run `git add <files>` first to stage your changes.")
        sys.exit(1)

    analysis = DiffParser.analyze(staged_diff)
    provider = get_provider(use_ai=not args.offline)

    print(f"{Style.DIM}Analyzing staged changes across {len(analysis.files)} files...{Style.RESET}")
    commit_msg = provider.generate_commit_message(analysis, staged_diff)

    print(f"\n{Style.BOLD}Generated Commit Message:{Style.RESET}")
    print(f"{Style.GREEN}{commit_msg}{Style.RESET}\n")

    if args.dry_run:
        print(f"{Style.DIM}[Dry-run mode: no commit was made]{Style.RESET}")
        return

    if args.yes:
        repo.commit(commit_msg)
        print(f"{Style.GREEN}✔ Successfully committed!{Style.RESET}")
        return

    try:
        choice = input(f"{Style.BOLD}Commit with this message? [Y/n/e(dit)]: {Style.RESET}").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(1)

    if choice in ["", "y", "yes"]:
        repo.commit(commit_msg)
        print(f"{Style.GREEN}✔ Successfully committed!{Style.RESET}")
    elif choice in ["e", "edit"]:
        custom = input("Enter custom subject line: ").strip()
        if custom:
            repo.commit(custom)
            print(f"{Style.GREEN}✔ Committed with custom message!{Style.RESET}")
        else:
            print("Commit canceled.")
    else:
        print("Commit canceled.")


def cmd_review(args):
    repo = GitRepo()
    diff = repo.get_staged_diff() if args.staged else repo.get_unstaged_diff()

    if not diff.strip():
        # Fallback to the other diff if one is empty
        diff = repo.get_staged_diff() if not args.staged else repo.get_unstaged_diff()

    if not diff.strip():
        print(f"{Style.YELLOW}No active changes detected to review.{Style.RESET}")
        return

    analysis = DiffParser.analyze(diff)
    provider = get_provider(use_ai=not args.offline)

    print(f"{Style.DIM}Running code review on {len(analysis.files)} modified files...{Style.RESET}")
    reviews = provider.review_changes(analysis, diff)

    if args.markdown:
        print(MarkdownFormatter.format_review_report(reviews))
    else:
        print(f"\n{Style.BOLD}Review Findings:{Style.RESET}")
        for r in reviews:
            lvl = r.get("level", "INFO")
            color = Style.RED if lvl == "CRITICAL" else (Style.YELLOW if lvl == "WARNING" else Style.GREEN)
            print(f" {color}[{lvl}]{Style.RESET} {Style.BOLD}{r.get('file')}{Style.RESET} ({r.get('category')}): {r.get('message')}")
        print()


def cmd_changelog(args):
    repo = GitRepo()
    commits = repo.get_recent_commits(count=args.count)

    if not commits:
        print(f"{Style.YELLOW}No commits found in history.{Style.RESET}")
        return

    print(f"{Style.DIM}Generating changelog from last {len(commits)} commits...{Style.RESET}\n")
    report = MarkdownFormatter.format_changelog(commits)
    print(report)


def cmd_status(args):
    repo = GitRepo()
    summary = repo.get_status_summary()
    branch = repo.get_current_branch()

    print(f"On branch: {Style.BOLD}{Style.CYAN}{branch}{Style.RESET}\n")
    print(f"Staged changes ({len(summary['staged'])}):")
    for f in summary["staged"]:
        print(f"  {Style.GREEN}+ {f}{Style.RESET}")

    print(f"\nUnstaged modifications ({len(summary['unstaged'])}):")
    for f in summary["unstaged"]:
        print(f"  {Style.YELLOW}* {f}{Style.RESET}")

    print(f"\nUntracked files ({len(summary['untracked'])}):")
    for f in summary["untracked"]:
        print(f"  {Style.DIM}? {f}{Style.RESET}")


def main():
    parser = argparse.ArgumentParser(
        prog="git-clarity",
        description="Git Clarity - AI-Native Git Diff Analyzer and PR Review Assistant"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # commit
    p_commit = subparsers.add_parser("commit", help="Generate conventional commit message and commit")
    p_commit.add_argument("-y", "--yes", action="store_true", help="Auto-accept and commit without prompt")
    p_commit.add_argument("-d", "--dry-run", action="store_true", help="Preview commit message only")
    p_commit.add_argument("--offline", action="store_true", help="Force local heuristic provider")

    # review
    p_review = subparsers.add_parser("review", help="Review staged or unstaged diffs for issues")
    p_review.add_argument("--staged", action="store_true", help="Review staged changes only")
    p_review.add_argument("-m", "--markdown", action="store_true", help="Output GitHub Markdown format")
    p_review.add_argument("--offline", action="store_true", help="Force local heuristic provider")

    # changelog
    p_cl = subparsers.add_parser("changelog", help="Generate Keep a Changelog markdown from commit history")
    p_cl.add_argument("-n", "--count", type=int, default=15, help="Number of recent commits to analyze")

    # status
    subparsers.add_parser("status", help="Show clean breakdown of staged and unstaged work")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "commit":
            cmd_commit(args)
        elif args.command == "review":
            cmd_review(args)
        elif args.command == "changelog":
            cmd_changelog(args)
        elif args.command == "status":
            cmd_status(args)
    except GitError as e:
        print(f"{Style.RED}Git Error:{Style.RESET} {e}")
        sys.exit(1)
    except Exception as e:
        print(f"{Style.RED}Unexpected Error:{Style.RESET} {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
