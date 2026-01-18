# Contributing to CVaR Portfolio Optimization

Thank you for your interest in contributing to this project! This document provides guidelines for contributions.

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/cvar-portfolio-optimization.git
   cd cvar-portfolio-optimization
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes (NumPy style)
- Keep functions focused and modular

Example:
```python
def calculate_cvar(
    returns: pd.DataFrame,
    weights: np.ndarray,
    beta: float
) -> Tuple[float, float]:
    """
    Calculate CVaR and VaR for a portfolio.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Historical returns data
    weights : np.ndarray
        Portfolio weights
    beta : float
        Confidence level (0 to 1)
        
    Returns
    -------
    cvar : float
        Conditional Value-at-Risk
    var : float
        Value-at-Risk
    """
    # Implementation
    pass
```

### Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting PR
  ```bash
  pytest tests/
  ```
- Aim for >80% code coverage

### Formatting

Run formatters before committing:
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Project Structure

```
cvar-portfolio-optimization/
├── src/                    # Source code
│   ├── cvar_optimizer.py   # Core optimization functions
│   ├── data_processing.py  # Data handling
│   ├── analysis.py         # Performance analysis
│   └── visualization.py    # Plotting functions
├── tests/                  # Unit tests
├── scripts/                # Executable scripts
├── notebooks/              # Jupyter notebooks
├── data/                   # Data files (not tracked)
├── results/                # Output files (not tracked)
└── docs/                   # Documentation

## Pull Request Process

1. **Update documentation**
   - Add docstrings to new functions
   - Update README.md if adding major features
   - Add examples to notebooks if appropriate

2. **Ensure tests pass**
   ```bash
   pytest tests/ -v
   ```

3. **Update CHANGELOG**
   - Document your changes in CHANGELOG.md

4. **Submit PR**
   - Provide clear description of changes
   - Reference any related issues
   - Request review from maintainers

## Types of Contributions

### Bug Reports

When reporting bugs, please include:
- Detailed description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- System information (Python version, OS, etc.)
- Code snippet demonstrating the bug

### Feature Requests

For feature requests:
- Explain the motivation and use case
- Provide examples of how it would be used
- Consider implementation complexity

### Documentation

Documentation improvements are always welcome:
- Fix typos or clarify explanations
- Add examples or tutorials
- Improve docstrings

### Code Contributions

Areas where contributions are especially welcome:
- Additional risk measures (e.g., drawdown, semi-deviation)
- Alternative optimization methods
- Performance improvements
- Better visualizations
- More comprehensive tests

## Code of Conduct

- Be respectful and professional
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions

## Questions?

Feel free to open an issue for questions or discussions!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
