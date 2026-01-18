# CVaR Portfolio Optimization

A comprehensive implementation of Conditional Value-at-Risk (CVaR) portfolio optimization using linear programming. This project explores risk-minimizing portfolio strategies and evaluates their performance under different market conditions.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Project Overview

This project implements a CVaR-minimizing portfolio optimization model based on the seminal paper ["Optimization of Conditional Value-at-Risk"](https://www.ise.ufl.edu/uryasev/files/2011/11/CVaR1_JOR.pdf) by Rockafellar and Uryasev (2000). The analysis uses historical stock data from 2019-2020 to explore how different risk management strategies perform during both stable and volatile market periods (pre-COVID vs. COVID-19 pandemic).

### Key Features

- **CVaR Minimization**: Linear programming formulation to minimize tail risk
- **Multi-Period Analysis**: Evaluates in-sample (2019) vs. out-of-sample (2020) performance
- **Parameter Sensitivity**: Examines impact of different confidence levels (β)
- **Risk Management Strategies**: Compares average vs. worst-case monthly CVaR minimization
- **Dynamic Rebalancing**: Implements monthly portfolio reoptimization with stability constraints
- **Comprehensive Visualization**: Detailed plots and analysis of portfolio composition and risk metrics

## 🎯 Research Questions

1. How does a CVaR-optimized portfolio perform out-of-sample during market turbulence?
2. How do different confidence levels (β) affect portfolio composition and risk?
3. Is minimizing average CVaR or worst-case monthly CVaR more effective?
4. Does monthly rebalancing improve risk-adjusted performance?
5. How can we enforce portfolio stability while maintaining risk minimization?

## 📊 Mathematical Formulation

### CVaR Optimization Model

Given portfolio weights **x** and historical returns **y**:

**Minimize:**
```
α + (1/(1-β)q) Σ u_k
```

**Subject to:**
- u_k ≥ -x^T y_k - α  (for all scenarios k)
- u_k ≥ 0
- Σ x_j = 1  (full investment)
- x_j ≥ 0  (no short selling)
- x^T ȳ ≥ R  (minimum expected return)

Where:
- β: confidence level (e.g., 0.95 for 95% confidence)
- α: Value-at-Risk (VaR)
- u_k: auxiliary variables capturing losses beyond VaR
- R: minimum required return threshold

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.8 or higher
Gurobi Optimizer (academic license available)
```

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/cvar-portfolio-optimization.git
cd cvar-portfolio-optimization
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up Gurobi license:**
   - Obtain a free [academic license](https://www.gurobi.com/academia/academic-program-and-licenses/)
   - Follow Gurobi's installation instructions

### Data Setup

Place your stock price data in the `data/` directory:
- `data/stocks2019.csv`: Training data (2019 stock prices)
- `data/stocks2020.csv`: Test data (2020 stock prices)

Expected format:
```
Date,AAPL,MSFT,GOOGL,...
2019-01-02,154.89,101.12,1045.23,...
...
```

## 📁 Project Structure

```
cvar-portfolio-optimization/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT license
├── .gitignore                  # Git ignore rules
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── cvar_optimizer.py       # Main optimization functions
│   ├── data_processing.py      # Data loading and preprocessing
│   ├── analysis.py             # Performance analysis functions
│   └── visualization.py        # Plotting and visualization
│
├── data/                       # Data directory (not tracked in git)
│   ├── .gitkeep
│   ├── stocks2019.csv          # Training data
│   └── stocks2020.csv          # Testing data
│
├── notebooks/                  # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_cvar_optimization.ipynb
│   ├── 03_sensitivity_analysis.ipynb
│   ├── 04_dynamic_rebalancing.ipynb
│   └── 05_final_analysis.ipynb
│
├── scripts/                    # Standalone scripts
│   ├── run_analysis.py         # Main analysis script
│   └── generate_report.py      # Generate PDF report
│
├── results/                    # Output directory
│   ├── figures/                # Generated plots
│   ├── portfolios/             # Saved portfolio weights
│   └── reports/                # Analysis reports
│
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_optimizer.py
│   └── test_data_processing.py
│
└── docs/                       # Documentation
    ├── methodology.md          # Detailed methodology
    ├── results_interpretation.md
    └── references.md           # Academic references
```

## 🏃 Usage

### Quick Start

Run the complete analysis pipeline:

```bash
python scripts/run_analysis.py
```

This will:
1. Load and preprocess the data
2. Run all optimization problems (Parts 2-6)
3. Generate visualizations
4. Save results to `results/` directory

### Jupyter Notebooks

For interactive analysis:

```bash
jupyter notebook
```

Navigate to `notebooks/` and run the notebooks in order.

### Custom Analysis

```python
from src.cvar_optimizer import solve_cvar_portfolio
from src.data_processing import load_and_process_data

# Load data
returns_2019, returns_2020 = load_and_process_data()

# Optimize portfolio
portfolio, cvar, var = solve_cvar_portfolio(
    returns_data=returns_2019,
    beta=0.95,
    R_target=0.0002
)

# Analyze performance
from src.analysis import evaluate_portfolio_performance

performance = evaluate_portfolio_performance(
    portfolio_weights=portfolio,
    test_returns=returns_2020
)
```

## 📈 Analysis Components

### Part 1: Data Preprocessing
- Calculate percentage returns from price data
- Handle missing values
- Separate NDX index from stock universe

### Part 2: Baseline CVaR Optimization (β=0.95)
- Optimize portfolio using 2019 data
- Evaluate out-of-sample performance on 2020 data
- Compare with NDX index benchmark
- Analyze non-stationarity effects

### Part 3: Sensitivity Analysis
- Test β = 0.90, 0.95, 0.99
- Examine how confidence level affects:
  - Portfolio concentration
  - Stock selection
  - Risk-return tradeoff

### Part 4: Worst-Case CVaR Optimization
- Minimize maximum monthly CVaR (robust optimization)
- Compare with average CVaR minimization
- Assess protection against extreme months

### Part 5: Dynamic Monthly Rebalancing
- Rolling 12-month window optimization
- Monthly portfolio updates throughout 2020
- Evaluate benefit of dynamic strategies

### Part 6: Portfolio Stability Analysis
- Identify unstable month-to-month allocations
- Implement stability constraints (max 5% change)
- Analyze cost of enforcing stability


## 🔬 Methodology

### CVaR vs VaR

**Value-at-Risk (VaR)**: The threshold loss value such that the probability of a loss exceeding this value is β.

**Conditional Value-at-Risk (CVaR)**: The expected loss given that the loss exceeds VaR. CVaR is:
- Coherent risk measure (satisfies subadditivity)
- Convex (enables efficient optimization)
- More conservative (accounts for tail losses)

### Linear Programming Formulation

The key insight from Rockafellar and Uryasev (2000) is that CVaR can be minimized through linear programming by introducing auxiliary variables u_k that capture losses beyond VaR.

### Rolling Window Approach

For monthly rebalancing, we use a 12-month rolling window:
- January 2020 portfolio: trained on Jan 2019 - Dec 2019
- February 2020 portfolio: trained on Feb 2019 - Jan 2020
- And so on...

This ensures the model always uses the most recent year of data while maintaining consistent sample size.

## 📚 References

1. Rockafellar, R. T., & Uryasev, S. (2000). "Optimization of conditional value-at-risk." *Journal of Risk*, 2, 21-42.

2. Rockafellar, R. T., & Uryasev, S. (2002). "Conditional value-at-risk for general loss distributions." *Journal of Banking & Finance*, 26(7), 1443-1471.

3. Pflug, G. C. (2000). "Some remarks on the value-at-risk and the conditional value-at-risk." In *Probabilistic constrained optimization* (pp. 272-281). Springer.

4. Artzner, P., Delbaen, F., Eber, J. M., & Heath, D. (1999). "Coherent measures of risk." *Mathematical Finance*, 9(3), 203-228.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Mohar Chaudhuri**
- MS Business Analytics, UT Austin McCombs
- Focus: Financial Analytics & Optimization
- [LinkedIn](https://www.linkedin.com/in/mohar-chaudhuri/) | [Email](moharchaudhuri.ofc@gmail.com)

## 🙏 Acknowledgments

- Paper by Rockafellar and Uryasev for the CVaR optimization formulation
- UT Austin McCombs School of Business
- Gurobi Optimization for their excellent solver and academic program


---

**Note**: This project was developed as part of the Optimization course at UT Austin McCombs School of Business. The code is designed to be reproducible and extensible for further research in portfolio optimization and risk management.
