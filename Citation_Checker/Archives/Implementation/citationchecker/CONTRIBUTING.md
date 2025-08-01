# Contributing to Citation Checker

Thank you for your interest in contributing to the Citation Checker project! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pytest for running tests

### Setting Up the Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/citationchecker.git
   cd citationchecker
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the tests to ensure everything is working:
   ```bash
   python -m pytest
   ```

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with the following information:

- A clear, descriptive title
- A detailed description of the bug
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Any relevant logs or error messages
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for enhancements! Please create an issue with:

- A clear, descriptive title
- A detailed description of the proposed enhancement
- Any relevant examples or use cases
- If applicable, references to similar features in other projects

### Pull Requests

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   or
   ```bash
   git checkout -b fix/your-bugfix-name
   ```

2. Make your changes, following the coding standards

3. Add or update tests as necessary

4. Run the tests to ensure they pass:
   ```bash
   python -m pytest
   ```

5. Commit your changes with a clear, descriptive commit message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```
   or
   ```bash
   git commit -m "Fix: your bugfix description"
   ```

6. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a pull request from your fork to the main repository

## Development Guidelines

### Testing

- All new features should include tests
- All bugfixes should include tests that reproduce the bug
- Run the full test suite before submitting a pull request
- Aim for high test coverage

### Documentation

- Update documentation for any changes to the API or functionality
- Include docstrings for all public functions, classes, and methods
- Keep the README and other documentation up to date

## Project Structure

Understanding the project structure will help you contribute effectively:

- `src/models/`: Data models for citations
- `src/parsers/`: Citation parsers for different formats
- `src/tests/`: Test suite
- `src/main.py`: Command-line interface

## Adding Support for New Citation Formats

One of the most valuable contributions is adding support for new citation formats. To add a new format:

1. Create a new parser class in `src/parsers/` that inherits from `BaseCitationParser`
2. Implement the required methods: `parse` and `extract_citations`
3. Add appropriate regex patterns for the new format
4. Create tests in `src/tests/` with sample citations in the new format
5. Update the factory method in `main.py` to support the new format
6. Update documentation to mention the new format

Example:

```python
# src/parsers/mla_parser.py
from src.parsers.base_parser import BaseCitationParser
from src.models.citation import Citation

class MLACitationParser(BaseCitationParser):
    def __init__(self):
        super().__init__()
        self.format_name = "mla"
        # Define regex patterns for MLA format
        
    def parse(self, text):
        # Implement parsing logic for MLA citations
        
    def extract_citations(self, text):
        # Implement extraction logic for MLA citations
```

## Review Process

All pull requests will be reviewed by the maintainers. The review process includes:

1. Checking that the code follows the style guidelines
2. Verifying that all tests pass
3. Ensuring the code is well-documented
4. Checking that the changes meet the project's goals and standards

## Community

We strive to maintain a welcoming and inclusive community. Please:

- Be respectful and considerate in all communications
- Focus on the code and ideas, not the person
- Help others when you can
- Be open to feedback and different perspectives

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

## Questions?

If you have any questions about contributing, please open an issue or contact the maintainers.

Thank you for contributing to Citation Checker!
