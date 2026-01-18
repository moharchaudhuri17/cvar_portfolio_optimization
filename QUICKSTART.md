# Quick Start Guide

Get up and running with CVaR portfolio optimization in 5 minutes.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cvar-portfolio-optimization.git
cd cvar-portfolio-optimization
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Gurobi

Get a free academic license from [Gurobi's website](https://www.gurobi.com/academia/academic-program-and-licenses/).

```bash
# After getting license
pip install gurobipy
grbgetkey YOUR-LICENSE-KEY
```

### 4. Add Your Data

Place your stock data in `data/` directory:
- `data/stocks2019.csv` - Training data
- `data/stocks2020.csv` - Test data

**Data format**: CSV with columns for Date and stock tickers.

## Basic Usage

### Option 1: Run Complete Analysis

```bash
python scripts/run_analysis.py
```

This will:
- Load and process data
- Run all optimization tasks
- Generate plots and save results

### Option 2: Use Python API

```python
from src import solve_cvar_portfolio, load_and_process_data

# Load data
stock_returns_2019, stock_returns_2020, _, _ = load_and_process_data()

# Optimize portfolio
weights, alpha, model = solve_cvar_portfolio(
    returns_data=stock_returns_2019,
    beta=0.95,           # 95% confidence level
    R_target=0.0002      # 0.02% minimum daily return
)

# View results
print(f"Optimal CVaR: {model.ObjVal:.6f}")
print(f"Number of positions: {sum(weights > 0.0001)}")
```

### Option 3: Use Jupyter Notebooks

```bash
jupyter notebook
```

Open `notebooks/` and explore interactive analysis.

## Example Workflow

### 1. Basic Portfolio Optimization

```python
import numpy as np
import pandas as pd
from src import solve_cvar_portfolio, calculate_cvar

# Load your data
returns = pd.read_csv('data/stocks2019.csv')
returns = returns.pct_change().dropna()

# Optimize
weights, alpha, model = solve_cvar_portfolio(
    returns_data=returns,
    beta=0.95,
    R_target=0.0002
)

# Print top holdings
top_stocks = np.argsort(weights)[-10:][::-1]
for i in top_stocks:
    if weights[i] > 0.001:
        print(f"{returns.columns[i]}: {weights[i]:.2%}")
```

### 2. Out-of-Sample Evaluation

```python
# Load test data
test_returns = pd.read_csv('data/stocks2020.csv')
test_returns = test_returns.pct_change().dropna()

# Evaluate portfolio on test data
cvar_test, var_test = calculate_cvar(test_returns, weights, beta=0.95)

print(f"Out-of-sample CVaR: {cvar_test:.6f}")
print(f"Out-of-sample VaR: {var_test:.6f}")
```

### 3. Compare Different Risk Levels

```python
results = {}
for beta in [0.90, 0.95, 0.99]:
    weights, _, model = solve_cvar_portfolio(
        returns_data=returns,
        beta=beta,
        R_target=0.0002
    )
    results[beta] = {
        'weights': weights,
        'cvar': model.ObjVal,
        'n_positions': sum(weights > 0.0001)
    }
    print(f"β={beta}: CVaR={model.ObjVal:.6f}, "
          f"Positions={results[beta]['n_positions']}")
```

### 4. Visualize Portfolio

```python
from src.visualization import plot_portfolio_weights

fig = plot_portfolio_weights(
    weights=weights,
    stock_names=returns.columns.tolist(),
    title="Optimal Portfolio (β=0.95)",
    top_n=15
)
fig.savefig('results/figures/my_portfolio.png', dpi=300, bbox_inches='tight')
```

## Common Tasks

### Change Optimization Parameters

```python
# More conservative (higher confidence level)
weights_conservative, _, _ = solve_cvar_portfolio(
    returns_data=returns,
    beta=0.99,        # 99% confidence
    R_target=0.0001   # Lower return requirement
)

# Less conservative
weights_aggressive, _, _ = solve_cvar_portfolio(
    returns_data=returns,
    beta=0.90,        # 90% confidence
    R_target=0.0005   # Higher return requirement
)
```

### Add Stability Constraints

```python
from src import solve_cvar_with_stability

# Optimize with max 5% weight change
weights_stable, _, _ = solve_cvar_with_stability(
    returns_data=new_returns,
    beta=0.95,
    R_target=0.0002,
    prev_weights=old_weights,
    max_change=0.05    # 5 percentage points
)
```

### Analyze Multiple Strategies

```python
from src.analysis import evaluate_portfolio_performance

# Compare different portfolios
performance = evaluate_portfolio_performance(
    weights=weights,
    train_returns=returns_2019,
    test_returns=returns_2020,
    beta=0.95
)

print(f"Train CVaR: {performance['train']['cvar']:.6f}")
print(f"Test CVaR: {performance['test']['cvar']:.6f}")
print(f"Deterioration: {performance['cvar_deterioration_pct']:.1f}%")
```

## Output Structure

After running analysis, you'll find:

```
results/
├── figures/              # All plots (.png)
│   ├── task2_portfolio_weights.png
│   ├── task3_beta_sensitivity.png
│   └── ...
├── portfolios/          # Portfolio weights (.csv)
│   ├── task2_portfolio_beta095.csv
│   ├── task3_portfolio_beta090.csv
│   └── ...
└── reports/             # Analysis reports (.pdf)
```

## Troubleshooting

### "Gurobi license not found"
- Make sure you've run `grbgetkey YOUR-LICENSE-KEY`
- Check that license file is in the correct location

### "ModuleNotFoundError: No module named 'src'"
- Make sure you're running from the project root directory
- Or install the package: `pip install -e .`

### "Optimization infeasible"
- Your R_target might be too high
- Try lowering minimum return requirement
- Check for data quality issues (NaN, infinite values)

### "Out of memory"
- Reduce number of scenarios (use weekly instead of daily data)
- Or optimize in batches

## Next Steps

- Read the full [documentation](docs/methodology.md)
- Explore [example notebooks](notebooks/)
- Check out the [API reference](docs/api_reference.md)
- Contribute! See [CONTRIBUTING.md](CONTRIBUTING.md)

## Getting Help

- Open an [issue](https://github.com/yourusername/cvar-portfolio-optimization/issues)
- Read the [FAQ](docs/faq.md)
- Email: your.email@example.com
