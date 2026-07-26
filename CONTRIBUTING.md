# Contributing to VA7

Thank you for considering contributing to VA7! This document outlines the process for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/my-feature`
4. Make your changes
5. Run tests to verify
6. Commit with a clear message
7. Push to your fork and submit a pull request

## Development Setup

```bash
# Clone and enter the repo
git clone https://github.com/YOUR_USERNAME/VA7.git
cd VA7

# Install dependencies
pip install -e "packages/va7-core[dev]"
pip install -e "packages/va7-identity[dev]"

# Run tests
cd packages/va7-core && pytest tests/ -v
cd packages/va7-identity && pytest tests/ -v
```

## Code Style

- Python 3.11+
- Follow existing code conventions
- Use type hints where practical
- Keep lines under 100 characters
- Run `ruff check` before committing

## Commit Messages

Use conventional commits:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `test:` adding or updating tests
- `refactor:` code refactoring
- `chore:` maintenance tasks

## Pull Requests

- One feature/fix per PR
- Include tests for new functionality
- Update documentation if needed
- Keep PRs focused and small
- Describe what changed and why

## Reporting Issues

Use GitHub Issues with the provided templates. Include:

- Python version
- Django version
- VA7 version
- Steps to reproduce
- Expected vs actual behavior

## Questions?

Open a Discussion on GitHub if you have questions before contributing.
