# Contributing

Thank you for your interest in contributing to Hyper-Extract!

## Ways to Contribute

### Report Bugs

Report bugs by opening a GitHub issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment information (Python version, OS, etc.)

### Suggest Features

We welcome feature suggestions! Please:
1. Check existing issues to avoid duplicates
2. Describe the use case clearly
3. Explain the expected behavior

### Contribute Code

#### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yifanfeng97/hyper-extract.git
   cd hyper-extract
   ```

3. Create a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # Windows: env\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

#### Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
3. Run tests:
   ```bash
   pytest tests/
   ```

4. Run linting:
   ```bash
   ruff check .
   ```

5. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```

6. Push and create a Pull Request

#### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests for new features

### Contribute Documentation

Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples
- Improve translations
- Update outdated content

### Translation Contributions

We welcome translation contributions:
1. Check the existing translations
2. Submit translations via PR

## Pull Request Guidelines

1. Reference related issues
2. Include tests for new features
3. Update documentation as needed
4. Follow the code style guidelines
5. Ensure all tests pass

## Development Resources

- [GitHub Repository](https://github.com/yifanfeng97/hyper-extract)
- [Issue Tracker](https://github.com/yifanfeng97/hyper-extract/issues)
- [Discussions](https://github.com/yifanfeng97/hyper-extract/discussions)

## Code of Conduct

Please be respectful and constructive in all interactions. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
