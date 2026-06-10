# Contributing to ContextSqueeze

Thank you for your interest in contributing to ContextSqueeze! We welcome contributions from the community.

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
2. **Make your changes** and ensure they follow our coding standards.
3. **Write tests** for any new functionality.
4. **Run the test suite** to ensure everything passes.
5. **Submit a pull request** with a clear description of your changes.

## Development Setup

```bash
git clone https://github.com/gitstq/contextsqueeze-py.git
cd contextsqueeze-py
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v --cov=contextsqueeze
```

## Code Style

We use `black` for formatting and `ruff` for linting:

```bash
black src/ tests/
ruff check src/ tests/
```

## Commit Message Convention

We follow the Angular commit message convention:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build process or auxiliary tool changes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
