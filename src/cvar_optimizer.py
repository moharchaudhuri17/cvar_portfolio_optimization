"""
CVaR Portfolio Optimization Module

This module implements Conditional Value-at-Risk (CVaR) portfolio optimization
using linear programming as described in Rockafellar and Uryasev (2000).
"""

import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
from typing import Tuple, Dict, Optional


def solve_cvar_portfolio(
    returns_data: pd.DataFrame,
    beta: float,
    R_target: float,
    verbose: bool = False
) -> Tuple[np.ndarray, float, gp.Model]:
    """
    Solve the CVaR portfolio optimization problem.
    
    Minimizes the β-CVaR of the portfolio subject to:
    - Portfolio weights sum to 1
    - No short selling (weights >= 0)
    - Expected return >= R_target
    
    Parameters
    ----------
    returns_data : pd.DataFrame
        Historical returns data (scenarios x stocks)
    beta : float
        Confidence level (e.g., 0.95 for 95% confidence)
    R_target : float
        Minimum required expected return
    verbose : bool, default=False
        Whether to print optimization output
        
    Returns
    -------
    weights_opt : np.ndarray
        Optimal portfolio weights
    alpha_opt : float
        Optimal VaR (Value-at-Risk)
    optMod : gp.Model
        Gurobi model object with solution
        
    References
    ----------
    Rockafellar, R. T., & Uryasev, S. (2000). "Optimization of conditional 
    value-at-risk." Journal of Risk, 2, 21-42.
    """
    q = len(returns_data)  # Number of scenarios
    Y = returns_data.values
    mean_returns = returns_data.mean().values
    n_stocks = len(returns_data.columns)
    
    # Initialize Gurobi model
    optMod = gp.Model("CVaR_Portfolio")
    
    # Decision variables
    optx = optMod.addMVar(shape=n_stocks, lb=0.0, name="x")  # Portfolio weights
    alpha = optMod.addVar(lb=-GRB.INFINITY, name="alpha")     # VaR threshold
    u = optMod.addMVar(shape=q, lb=0, name="u")              # Auxiliary variables
    
    # Constraints
    # 1) Portfolio weights sum to 1
    optMod.addConstr(optx.sum() == 1, name="weights_sum")
    
    # 2) u_k >= -x^T*y_k - alpha (linearization of [·]+ terms)
    optMod.addConstr(u >= -Y @ optx - alpha, name="u_constraint")
    
    # 3) Expected return constraint
    optMod.addConstr(mean_returns @ optx >= R_target, name="min_return")
    
    # Objective: minimize CVaR
    # CVaR = alpha + 1/((1-beta)*q) * sum(u_k)
    optMod.setObjective(
        alpha + (1/((1-beta)*q)) * u.sum(),
        GRB.MINIMIZE
    )
    
    # Optimization settings
    optMod.Params.OutputFlag = 1 if verbose else 0
    optMod.optimize()
    
    # Check optimization status
    if optMod.Status != GRB.OPTIMAL:
        print(f"Warning: Optimization not optimal. Status: {optMod.Status}")
        if optMod.Status == GRB.INFEASIBLE:
            print("Model is infeasible. Consider relaxing constraints.")
    
    # Extract results
    weights_opt = optx.X
    alpha_opt = alpha.X
    
    return weights_opt, alpha_opt, optMod


def solve_cvar_minimax(
    returns_data: pd.DataFrame,
    beta: float,
    R_target: float,
    monthly_splits: list,
    verbose: bool = False
) -> Tuple[np.ndarray, float, gp.Model]:
    """
    Solve the minimax CVaR portfolio optimization problem.
    
    Minimizes the maximum monthly CVaR across all months rather than
    the average CVaR. This provides more robust protection against
    worst-case scenarios.
    
    Parameters
    ----------
    returns_data : pd.DataFrame
        Historical returns data
    beta : float
        Confidence level
    R_target : float
        Minimum required expected return
    monthly_splits : list
        List of tuples (start_idx, end_idx) for each month
    verbose : bool, default=False
        Whether to print optimization output
        
    Returns
    -------
    weights_opt : np.ndarray
        Optimal portfolio weights
    max_cvar_opt : float
        Optimal maximum monthly CVaR
    optMod : gp.Model
        Gurobi model object
    """
    Y = returns_data.values
    mean_returns = returns_data.mean().values
    n_stocks = len(returns_data.columns)
    n_months = len(monthly_splits)
    
    # Initialize model
    optMod = gp.Model("CVaR_Minimax")
    
    # Decision variables
    optx = optMod.addMVar(shape=n_stocks, lb=0.0, name="x")
    z = optMod.addVar(lb=-GRB.INFINITY, name="z")  # Maximum CVaR across months
    
    # For each month, add constraints
    alpha_vars = []
    u_vars = []
    
    for m, (start_idx, end_idx) in enumerate(monthly_splits):
        Y_month = Y[start_idx:end_idx]
        q_month = len(Y_month)
        
        # Add alpha and u variables for this month
        alpha_m = optMod.addVar(lb=-GRB.INFINITY, name=f"alpha_{m}")
        u_m = optMod.addMVar(shape=q_month, lb=0, name=f"u_{m}")
        
        alpha_vars.append(alpha_m)
        u_vars.append(u_m)
        
        # Constraint: u_m_k >= -x^T*y_k - alpha_m
        optMod.addConstr(u_m >= -Y_month @ optx - alpha_m, name=f"u_month_{m}")
        
        # Constraint: z >= CVaR for this month
        cvar_month = alpha_m + (1/((1-beta)*q_month)) * u_m.sum()
        optMod.addConstr(z >= cvar_month, name=f"max_cvar_{m}")
    
    # Portfolio constraints
    optMod.addConstr(optx.sum() == 1, name="weights_sum")
    optMod.addConstr(mean_returns @ optx >= R_target, name="min_return")
    
    # Objective: minimize maximum CVaR
    optMod.setObjective(z, GRB.MINIMIZE)
    
    optMod.Params.OutputFlag = 1 if verbose else 0
    optMod.optimize()
    
    if optMod.Status != GRB.OPTIMAL:
        print(f"Warning: Optimization not optimal. Status: {optMod.Status}")
    
    weights_opt = optx.X
    max_cvar_opt = z.X
    
    return weights_opt, max_cvar_opt, optMod


def solve_cvar_with_stability(
    returns_data: pd.DataFrame,
    beta: float,
    R_target: float,
    prev_weights: Optional[np.ndarray] = None,
    max_change: float = 0.05,
    verbose: bool = False
) -> Tuple[np.ndarray, float, gp.Model]:
    """
    Solve CVaR optimization with stability constraints.
    
    Adds constraints to limit how much each portfolio weight can change
    from the previous period, enforcing portfolio stability.
    
    Parameters
    ----------
    returns_data : pd.DataFrame
        Historical returns data
    beta : float
        Confidence level
    R_target : float
        Minimum required expected return
    prev_weights : np.ndarray, optional
        Previous period's portfolio weights
    max_change : float, default=0.05
        Maximum allowed change in any weight (e.g., 0.05 = 5 percentage points)
    verbose : bool, default=False
        Whether to print optimization output
        
    Returns
    -------
    weights_opt : np.ndarray
        Optimal portfolio weights
    alpha_opt : float
        Optimal VaR
    optMod : gp.Model
        Gurobi model object
    """
    q = len(returns_data)
    Y = returns_data.values
    mean_returns = returns_data.mean().values
    n_stocks = len(returns_data.columns)
    
    # Initialize model
    optMod = gp.Model("CVaR_Stable")
    
    # Decision variables
    optx = optMod.addMVar(shape=n_stocks, lb=0.0, name="x")
    alpha = optMod.addVar(lb=-GRB.INFINITY, name="alpha")
    u = optMod.addMVar(shape=q, lb=0, name="u")
    
    # Standard CVaR constraints
    optMod.addConstr(optx.sum() == 1, name="weights_sum")
    optMod.addConstr(u >= -Y @ optx - alpha, name="u_constraint")
    optMod.addConstr(mean_returns @ optx >= R_target, name="min_return")
    
    # Stability constraints
    if prev_weights is not None:
        for i in range(n_stocks):
            # Lower bound: x_i >= prev_x_i - max_change
            optMod.addConstr(
                optx[i] >= max(0, prev_weights[i] - max_change),
                name=f"stability_lb_{i}"
            )
            # Upper bound: x_i <= prev_x_i + max_change
            optMod.addConstr(
                optx[i] <= min(1, prev_weights[i] + max_change),
                name=f"stability_ub_{i}"
            )
    
    # Objective
    optMod.setObjective(
        alpha + (1/((1-beta)*q)) * u.sum(),
        GRB.MINIMIZE
    )
    
    optMod.Params.OutputFlag = 1 if verbose else 0
    optMod.optimize()
    
    if optMod.Status != GRB.OPTIMAL:
        print(f"Warning: Optimization not optimal. Status: {optMod.Status}")
    
    weights_opt = optx.X
    alpha_opt = alpha.X
    
    return weights_opt, alpha_opt, optMod


def calculate_cvar(
    returns: pd.DataFrame,
    weights: np.ndarray,
    beta: float
) -> Tuple[float, float]:
    """
    Calculate CVaR and VaR for a given portfolio.
    
    This function computes the CVaR without optimization - useful for
    evaluating a portfolio on out-of-sample data.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Returns data
    weights : np.ndarray
        Portfolio weights
    beta : float
        Confidence level
        
    Returns
    -------
    cvar_val : float
        Conditional Value-at-Risk
    var_val : float
        Value-at-Risk
    """
    # Calculate portfolio returns
    portfolio_returns = np.dot(returns.values, weights)
    portfolio_losses = -portfolio_returns
    
    # Calculate VaR as the beta-th percentile of losses
    var_val = np.percentile(portfolio_losses, beta * 100)
    
    # Calculate CVaR as mean of losses exceeding VaR
    tail_losses = portfolio_losses[portfolio_losses >= var_val]
    cvar_val = np.mean(tail_losses) if len(tail_losses) > 0 else var_val
    
    return cvar_val, var_val


def split_returns_by_month(returns: pd.DataFrame, year: int) -> Dict[str, Tuple[int, int]]:
    """
    Split returns data into monthly chunks.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Returns data with DatetimeIndex
    year : int
        Year to split
        
    Returns
    -------
    monthly_splits : dict
        Dictionary mapping 'YYYY-MM' to (start_idx, end_idx) tuples
    """
    monthly_splits = {}
    
    for month in range(1, 13):
        month_mask = (returns.index.year == year) & (returns.index.month == month)
        if month_mask.sum() > 0:
            indices = np.where(month_mask)[0]
            start_idx, end_idx = indices[0], indices[-1] + 1
            monthly_splits[f"{year}-{month:02d}"] = (start_idx, end_idx)
    
    return monthly_splits
