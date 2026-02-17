# Contributing to Google Maps Coordinate Extractor

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🎯 Ways to Contribute

### 🐛 Report Bugs

- Check if the bug has already been reported in [Issues](../../issues)
- If not, create a new issue with:
  - Clear title and description
  - Steps to reproduce
  - Expected vs actual behavior
  - Your environment (OS, Python version, Chrome version)
  - Relevant logs (use `--log-level DEBUG`)

### 💡 Suggest Features

- Check [existing feature requests](../../issues?q=is%3Aissue+label%3Aenhancement)
- Create a new issue describing:
  - The problem you're trying to solve
  - Your proposed solution
  - Alternative solutions you've considered
  - Any additional context

### 📝 Improve Documentation

- Fix typos or clarify existing docs
- Add examples or use cases
- Improve code comments
- Translate documentation

### 🔧 Submit Code

See the Development section below

## 🛠️ Development Setup

1. **Fork and clone the repository**:

   ```bash
   git clone https://github.com/YOUR_USERNAME/coordinate-extractor.git
   cd coordinate-extractor
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Test your changes** thoroughly:

   ```bash
   # Test basic functionality
   python fetch_coordinates.py places_template.json --force

   # Test with different options
   python fetch_coordinates.py places_template.json --output-format csv
   python fetch_coordinates.py places_template.json --log-level DEBUG
   ```

3. **Follow code style**:
   - Use meaningful variable names
   - Add docstrings to functions
   - Keep functions focused and small
   - Follow PEP 8 style guidelines

4. **Commit your changes**:

   ```bash
   git add .
   git commit -m "feat: add feature description"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `refactor:` for code refactoring
   - `test:` for adding tests
   - `chore:` for maintenance tasks

5. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**:
   - Provide a clear title and description
   - Reference any related issues
   - Explain what you changed and why

## 🎨 Code Style Guidelines

- **Python**: Follow PEP 8
- **Line length**: Max 100 characters
- **Imports**: Group standard library, third-party, and local imports
- **Comments**: Explain _why_, not _what_
- **Logging**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)

## 🧪 Testing Guidelines

While we don't have automated tests yet (contributions welcome!), please manually test:

1. **Basic functionality**: Does it extract coordinates?
2. **Error handling**: Does it handle missing URLs gracefully?
3. **Edge cases**: Empty files, invalid JSON, network errors
4. **Different formats**: JSON and CSV output
5. **Retry logic**: Does it retry on failures?
6. **Validation**: Does it catch invalid coordinates?

## 📚 Documentation Guidelines

- Keep README concise and scannable
- Use examples liberally
- Update the roadmap when adding features
- Add inline code comments for complex logic
- Update CHANGELOG.md (if exists) with your changes

## 🚀 Feature Priorities

See the [Roadmap](README.md#-roadmap) in README for planned features. High-priority items:

1. GeoJSON/KML export formats
2. Configuration file support
3. Parallel processing
4. Unit tests
5. Docker support

## 🤔 Questions?

- Open a [Discussion](../../discussions) for general questions
- Open an [Issue](../../issues) for bug reports or feature requests
- Check existing issues and discussions first

## 📜 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help others learn and grow

## 🙏 Thank You!

Every contribution, no matter how small, helps make this project better for everyone. We appreciate your time and effort!
