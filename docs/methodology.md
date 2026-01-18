# Methodology

## Overview

This document provides a detailed explanation of the mathematical formulation and implementation of the CVaR portfolio optimization model.

## Conditional Value-at-Risk (CVaR)

### Definitions

**Value-at-Risk (VaR)**: The VaR at confidence level β represents the threshold loss such that:
```
P(Loss ≤ VaR_β) = β
```

For example, VaR at 95% confidence is the loss level that will not be exceeded 95% of the time.

**Conditional Value-at-Risk (CVaR)**: CVaR, also called Expected Shortfall or Tail VaR, is the expected loss given that the loss exceeds VaR:
```
CVaR_β = E[Loss | Loss ≥ VaR_β]
```

### Why CVaR?

CVaR has several advantages over VaR:

1. **Coherent Risk Measure**: CVaR satisfies all axioms of coherent risk measures:
   - Monotonicity
   - Subadditivity (risk of portfolio ≤ sum of individual risks)
   - Positive homogeneity
   - Translation invariance

2. **Convex**: CVaR is a convex function of portfolio weights, enabling efficient optimization

3. **Captures Tail Risk**: CVaR accounts for the severity of losses beyond VaR, not just the probability

4. **Computationally Tractable**: Can be minimized via linear programming

## Mathematical Formulation

### Portfolio Notation

- **x** = (x₁, x₂, ..., xₙ): Portfolio weights (decision variables)
- **y** = (y₁, y₂, ..., yₙ): Random vector of asset returns
- Portfolio return: **x**ᵀ**y** = Σᵢ xᵢyᵢ
- Portfolio loss: -**x**ᵀ**y**

### CVaR Optimization Formula

For a given portfolio **x**, the β-CVaR is:

```
F_β(x) = min_α { α + 1/(1-β) E[(−x^T y − α)₊] }
```

where:
- α is a decision variable representing VaR
- (t)₊ = max(t, 0) is the positive part function
- E[·] denotes expectation

### Discrete Approximation

In practice, we approximate the expectation using historical scenarios:

```
F̃_β(x) = min_α { α + 1/((1-β)q) Σₖ₌₁ᵍ (−x^T yₖ − α)₊ }
```

where:
- q = number of scenarios (historical observations)
- yₖ = returns in scenario k

### Linearization

The (·)₊ terms make the problem nonlinear. We linearize by introducing auxiliary variables uₖ:

```
Minimize: α + 1/((1-β)q) Σₖ₌₁ᵍ uₖ

Subject to:
  uₖ ≥ −x^T yₖ − α    for all k = 1, ..., q
  uₖ ≥ 0             for all k
  Σᵢ xᵢ = 1          (full investment)
  xᵢ ≥ 0             for all i (no short selling)
  x^T μ ≥ R          (minimum expected return)
```

where μ is the vector of mean returns.

This is now a **linear program** that can be solved efficiently using standard LP solvers like Gurobi.

## Extensions

### 1. Minimax CVaR

Instead of minimizing average CVaR, we can minimize the maximum CVaR across different time periods:

```
Minimize: z

Subject to:
  z ≥ CVaR_t(x)    for all periods t
  (plus standard portfolio constraints)
```

This provides more robust protection against worst-case scenarios.

### 2. Stability Constraints

To prevent excessive portfolio turnover, we can add constraints limiting how much weights can change between periods:

```
|xᵢ^(t+1) − xᵢ^(t)| ≤ δ    for all assets i
```

where δ is the maximum allowed change (e.g., 0.05 for 5 percentage points).

### 3. Transaction Costs

We can incorporate proportional transaction costs:

```
Cost = c · Σᵢ |xᵢ^(t+1) − xᵢ^(t)|
```

This leads to a piecewise linear objective that remains solvable as an LP.

## Implementation Details

### Gurobi Formulation

Our implementation uses Gurobi's Python API:

```python
import gurobipy as gp
from gurobipy import GRB

# Create model
model = gp.Model("CVaR_Portfolio")

# Decision variables
x = model.addMVar(n_stocks, lb=0.0)          # weights
alpha = model.addVar(lb=-GRB.INFINITY)        # VaR
u = model.addMVar(q, lb=0)                    # auxiliary variables

# Constraints
model.addConstr(x.sum() == 1)                 # full investment
model.addConstr(u >= -Y @ x - alpha)          # CVaR constraints
model.addConstr(mean_returns @ x >= R)        # min return

# Objective
model.setObjective(
    alpha + (1/((1-beta)*q)) * u.sum(),
    GRB.MINIMIZE
)

model.optimize()
```

### Computational Complexity

For a portfolio with:
- n assets
- q scenarios (historical days)

The LP has:
- Decision variables: n + 1 + q (portfolio weights + α + auxiliary variables)
- Constraints: O(q) (mainly from u constraints)

Modern LP solvers like Gurobi can handle problems with n=100 and q=250 (one year of daily data) in under 1 second.

## References

1. **Rockafellar, R. T., & Uryasev, S. (2000)**. "Optimization of conditional value-at-risk." *Journal of Risk*, 2, 21-42.
   - Original paper introducing LP formulation of CVaR optimization

2. **Rockafellar, R. T., & Uryasev, S. (2002)**. "Conditional value-at-risk for general loss distributions." *Journal of Banking & Finance*, 26(7), 1443-1471.
   - Extensions to general distributions

3. **Pflug, G. C. (2000)**. "Some remarks on the value-at-risk and the conditional value-at-risk." In *Probabilistic constrained optimization* (pp. 272-281). Springer.
   - Theoretical properties of CVaR

4. **Artzner, P., Delbaen, F., Eber, J. M., & Heath, D. (1999)**. "Coherent measures of risk." *Mathematical Finance*, 9(3), 203-228.
   - Axioms of coherent risk measures

5. **Krokhmal, P., Palmquist, J., & Uryasev, S. (2002)**. "Portfolio optimization with conditional value-at-risk objective and constraints." *Journal of Risk*, 4, 43-68.
   - Applications to portfolio optimization

## Appendix: Key Theorems

### Theorem 1 (Rockafellar & Uryasev, 2000)

For any portfolio **x** and confidence level β ∈ (0,1):

```
CVaR_β(x) = min_α { α + 1/(1-β) E[(−x^T y − α)₊] }
```

The minimizer α* equals VaR_β(x).

### Theorem 2 (Coherence of CVaR)

CVaR satisfies:
1. **Subadditivity**: CVaR(X + Y) ≤ CVaR(X) + CVaR(Y)
2. **Positive homogeneity**: CVaR(λX) = λ CVaR(X) for λ ≥ 0
3. **Monotonicity**: If X ≤ Y almost surely, then CVaR(X) ≤ CVaR(Y)
4. **Translation invariance**: CVaR(X + c) = CVaR(X) + c

This makes CVaR superior to VaR, which fails subadditivity.

### Theorem 3 (Convexity)

CVaR is a convex function of portfolio weights **x**. Combined with linear constraints, this guarantees a convex optimization problem with a unique global minimum.
