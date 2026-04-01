# Contributing

Contributions are welcome. Please follow these guidelines:

## Development Setup

```bash
git clone https://github.com/jramirezgen/multiscale-route-hypothesis-platform.git
cd multiscale-route-hypothesis-platform
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Style

- Follow PEP 8
- Use type hints where practical
- Keep functions focused and testable

## Frozen Models Policy

Parameters in `src/mrhp/models/frozen.py` are version-locked.
Do not modify frozen parameters without creating a new version tag.

## Pull Requests

1. Fork the repo
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a PR with a clear description
