# Contributing Guide

Thank you for your interest in contributing to the Automated Security Update tool!

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Drupal development environment
- Jenkins (for pipeline testing)

### Local Development

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/your-username/automated-security-update.git
cd automated-security-update
```

3. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

5. Set up pre-commit hooks:
```bash
pre-commit install
```

## Code Style

### Python

We follow PEP 8 with some modifications:

- Line length: 100 characters
- Use type hints for all functions
- Use docstrings for all public functions
- Use f-strings for string formatting

**Example**:
```python
from __future__ import annotations

from pathlib import Path
from typing import Any


def process_data(input_path: Path, config: dict[str, Any]) -> dict[str, Any]:
    """
    Process data from input file.
    
    Args:
        input_path: Path to input file
        config: Configuration dictionary
        
    Returns:
        Processed data dictionary
        
    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Implementation
    return {}
```

### Shell Scripts

- Use `#!/bin/bash` shebang
- Use `set -e` for error handling
- Quote all variables: `"$VARIABLE"`
- Use meaningful variable names in UPPER_CASE

**Example**:
```bash
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Processing in: $PROJECT_ROOT"
```

## Testing

### Unit Tests

Run unit tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=core tests/
```

### Integration Tests

Test against a real Drupal site:
```bash
export DRUPAL_ROOT=/path/to/drupal
export SITE_URL=http://localhost
pytest tests/integration/
```

### Linting

```bash
# Python
flake8 core/
mypy core/
black --check core/

# Shell
shellcheck scripts/*.sh
```

## Making Changes

### Branch Naming

- Feature: `feature/description`
- Bug fix: `bugfix/description`
- Documentation: `docs/description`

**Examples**:
- `feature/add-slack-notifications`
- `bugfix/fix-composer-timeout`
- `docs/update-installation-guide`

### Commit Messages

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

**Examples**:
```
feat(ai-fix): Add support for Anthropic Claude

- Implement Claude API integration
- Add configuration options
- Update documentation

Closes #123
```

```
fix(testing): Handle null watchdog entries

Previously, null entries in watchdog logs would cause
the testing engine to crash. Now they are safely ignored.

Fixes #456
```

### Pull Request Process

1. Create a feature branch
2. Make your changes
3. Add/update tests
4. Update documentation
5. Run linters and tests
6. Push to your fork
7. Create a pull request

**PR Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests pass
- [ ] No new warnings
```

## Adding New Features

### Adding a New Engine

1. Create file in `core/`:
```python
# core/new_engine.py
from __future__ import annotations

from pathlib import Path

from .config import load_config
from .logger import setup_logger


def run_new_engine() -> Path:
    """Execute new engine functionality."""
    config = load_config()
    logger = setup_logger("new_engine", config.logs_dir)
    
    logger.info("Starting new engine")
    
    # Implementation
    
    report_path = config.reports_dir / "new-engine-results.json"
    logger.info("Report written to %s", report_path)
    return report_path


if __name__ == "__main__":
    run_new_engine()
```

2. Add tests:
```python
# tests/test_new_engine.py
from core.new_engine import run_new_engine


def test_run_new_engine(tmp_path, monkeypatch):
    monkeypatch.setenv("DRUPAL_ROOT", str(tmp_path))
    result = run_new_engine()
    assert result.exists()
```

3. Update documentation
4. Add to Jenkins pipeline if needed

### Adding Configuration Options

1. Update `core/config.py`:
```python
@dataclass(frozen=True)
class Config:
    # ... existing fields ...
    new_option: str
```

2. Update `config/config.example.yaml`:
```yaml
new_section:
  new_option: "default_value"
```

3. Update `.env.example`:
```bash
NEW_OPTION=default_value
```

4. Document in README.md

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Short description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
        
    Example:
        >>> function_name("test", 42)
        True
    """
```

### README Updates

When adding features, update:
- Feature list
- Usage examples
- Configuration options
- Troubleshooting section

### Architecture Documentation

Update `ARCHITECTURE.md` for:
- New components
- Changed data flows
- New dependencies

## Release Process

### Version Numbering

We use Semantic Versioning (SemVer):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Creating a Release

1. Update version in `__version__.py`
2. Update CHANGELOG.md
3. Create git tag:
```bash
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

4. Create GitHub release with notes

## Code Review Guidelines

### For Contributors

- Keep PRs focused and small
- Write clear descriptions
- Respond to feedback promptly
- Update based on review comments

### For Reviewers

- Be constructive and respectful
- Focus on code quality and maintainability
- Check for test coverage
- Verify documentation updates

## Getting Help

- **Questions**: Open a discussion
- **Bugs**: Create an issue
- **Features**: Create an issue with proposal
- **Security**: Email security@example.com

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing private information

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md
- Release notes
- Project documentation

Thank you for contributing! 🎉
