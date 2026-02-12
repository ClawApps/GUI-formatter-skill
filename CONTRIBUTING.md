[English](CONTRIBUTING.md) | [中文](CONTRIBUTING_zh.md)

# Contributing to GUI Formatter

Thank you for your interest in contributing! This guide will help you get started.

## How to Contribute

### Reporting Bugs

1. Search [existing issues](https://github.com/ClawApps/GUI-formatter-skill/issues) to avoid duplicates
2. Use the **Bug Report** template when creating a new issue
3. Include: steps to reproduce, expected behavior, actual behavior, and your environment

### Suggesting Features

1. Open an issue using the **Feature Request** template
2. Describe the use case and why it would be valuable
3. If possible, include examples of the expected input/output

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature
   ```
3. Make your changes following the code style guidelines below
4. Test your changes:
   ```bash
   python scripts/formatter.py    # Run formatter self-test
   python scripts/validator.py    # Run validator self-test
   python scripts/catalog.py      # Run catalog self-test
   ```
5. Commit with a clear message (see commit conventions below)
6. Push and open a PR against `main`

## Development Setup

```bash
# Clone
git clone https://github.com/ClawApps/GUI-formatter-skill.git
cd GUI-formatter-skill

# No dependencies to install - pure Python 3.8+ standard library

# Run self-tests
python scripts/formatter.py
python scripts/validator.py
python scripts/catalog.py
```

## Project Structure

```
scripts/
├── formatter.py    # Core formatting engine (intent -> UITree)
├── catalog.py      # Component registry (whitelist)
├── validator.py    # 3-round validation + Markdown fallback
└── actions.py      # Action type definitions

references/         # Documentation for component props, actions, validation rules
SKILL.md            # Claude Code Skill definition
```

## Code Style

- Python 3.8+ compatible (no walrus operator, no `match` statements)
- Use type hints for function signatures
- Use docstrings for classes and public methods
- Keep imports minimal - standard library only, no external dependencies
- Follow existing naming conventions (snake_case for functions/variables, PascalCase for classes)

## Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new component type
fix: correct Form field validation
docs: update component-catalog examples
refactor: simplify intent parsing logic
test: add edge case tests for validator
```

## Adding a New Component

1. Register the component in `scripts/catalog.py` (`_register_builtin_components`)
2. Add an intent handler in `scripts/formatter.py` if needed
3. Update `SKILL.md` - component list, intent mapping table, component count
4. Update `references/component-catalog.md` - full property table and examples
5. Update `references/fallback-strategies.md` - component list
6. Update `README.md` and `README_zh.md` - component tables and counts

## Questions?

Open an issue with the **Question** label and we'll be happy to help.
