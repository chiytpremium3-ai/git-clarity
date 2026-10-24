# Contributing to Git Clarity

Thank you for your interest in contributing to **Git Clarity**! We welcome all contributions, including bug reports, feature requests, documentation improvements, and code changes.

## Development Workflow

1. **Fork and Clone** the repository:
   ```bash
   git clone https://github.com/<your-username>/git-clarity.git
   cd git-clarity
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -e ".[dev,ai]"
   ```

3. **Run the test suite**:
   ```bash
   python3 -m unittest discover -s tests
   ```

## Pull Request Guidelines

- Ensure all existing tests pass before opening a PR.
- Add unit tests for new features or bug fixes under `tests/`.
- Follow [Conventional Commits](https://www.conventionalcommits.org/) for your commit messages (you can use `git-clarity commit` to do this!).
- Update the documentation in `README.md` if any CLI flags or behaviours change.

## Code of Conduct

Please maintain a polite, respectful, and collaborative environment. All contributors are expected to uphold open-source community standards.
