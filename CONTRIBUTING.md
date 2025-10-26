# Contributing to Netplan YAML Generator

Thank you for your interest in contributing to the Netplan YAML Generator! This document provides guidelines for contributing to the project.

## Code of Conduct

This project follows a simple code of conduct: be respectful, constructive, and helpful to all contributors and users.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check existing issues to avoid duplicates
2. Create a new issue with:
   - Clear description of the problem or feature
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Python version)
   - Example netplan configuration (if applicable)

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed
4. **Test your changes**
   ```bash
   python test_simple.py
   python test_generator.py
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add feature: description of your changes"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Write clear, descriptive docstrings
- Keep functions focused and single-purpose
- Use meaningful variable and function names

### Testing

- Add tests for new features
- Ensure existing tests pass
- Test with various netplan configurations
- Validate generated YAML syntax

### Documentation

- Update README.md for new features
- Add examples for new functionality
- Update CHANGELOG.md
- Include docstrings for new functions/classes

## License

By contributing to this project, you agree that your contributions will be licensed under the GNU General Public License v3.0.

All contributions must include the appropriate copyright header:

```python
"""
Copyright (C) 2025 Michael Tinsay

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""
```

## Areas for Contribution

### High Priority
- Additional netplan features (VLANs, tunnels, etc.)
- More comprehensive test coverage
- Performance optimizations
- Better error handling and validation

### Medium Priority
- Additional output formats (JSON, etc.)
- Configuration file input support
- Interactive mode
- More bond/bridge parameters

### Low Priority
- GUI interface
- Integration with network management tools
- Additional renderers support

## Getting Help

If you need help with development:

1. Check the existing documentation
2. Look at example code in the repository
3. Create an issue with your question
4. Reference the netplan documentation: https://netplan.io/

## Recognition

Contributors will be recognized in the project documentation and release notes.

Thank you for helping make this project better!