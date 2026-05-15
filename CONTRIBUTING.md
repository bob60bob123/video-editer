# Contributing to Video Editor

Thank you for your interest in contributing!

## How to Contribute

### Reporting Bugs

- Use the GitHub Issues page
- Include your OS version, Python version, and FFmpeg version
- Provide steps to reproduce the issue
- Include error messages and screenshots if applicable

### Suggesting Features

- Open a GitHub Issue with the `enhancement` label
- Describe the feature and its use case
- Explain why it would be beneficial to the project

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or fix
3. Write your code
4. Test thoroughly on Windows
5. Submit a pull request with a clear description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/video-make.git
cd video-make

# Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install PyQt5

# Run the application
python main.py
```

## Code Style

- Use UTF-8 encoding with `# -*- coding: utf-8 -*-`
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add comments for complex logic

## Adding Translations

To add a new language:

1. Add a new language section in `i18n.py`
2. Add all translation keys with the new language values
3. Update the `T()` function to support the new language
4. Test all UI elements in the new language

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
