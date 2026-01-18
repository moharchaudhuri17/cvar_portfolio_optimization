"""
Portfolio Analysis Module

Functions for evaluating portfolio performance, comparing strategies,
and analyzing risk metrics.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
from .cvar_optimizer import calculate_cvar


def evaluate_portfolio_performance(
    weights: np.ndarray,
    train_returns: pd.DataFrame,
    test_returns: pd.DataFrame,
    beta: float = 0.95,
    index_returns_train: pd.Series = None,
    index_returns_test: pd.Series = None
) -> Dict:
    """
    Comprehensive performance evaluation of a portfolio.
    
    Parameters
    ----------
    weights : np.ndarray
        Portfolio weights
    train_returns : pd.DataFrame
        In-sample returns data
    test_returns : pd.DataFrame
        Out-of-sample returns data
    beta : float, default=0.95
        Confidence level for CVaR
    index_returns_train : pd.Series, optional
        Benchmark index returns (in-sample)
    index_returns_test : pd.Series, optional
        Benchmark index returns (out-of-sample)
        
    Returns
    -------
    performance : dict
        Dictionary with performance metrics
    """
    # Portfolio returns
    portfolio_returns_train = np.dot(train_returns.values, weights)
    portfolio_returns_test = np.dot(test_returns.values, weights)
    
    # In-sample metrics
    cvar_train, var_train = calculate_cvar(train_returns, weights, beta)
    mean_return_train = np.mean(portfolio_returns_train)
    std_train = np.std(portfolio_returns_train)
    sharpe_train = mean_return_train / std_train if std_train > 0 else 0
    
    # Out-of-sample metrics
    cvar_test, var_test = calculate_cvar(test_returns, weights, beta)
    mean_return_test = np.mean(portfolio_returns_test)
    std_test = np.std(portfolio_returns_test)
    sharpe_test = mean_return_test / std_test if std_test > 0 else 0
    
    # CVaR deterioration
    cvar_deterioration = ((cvar_test / cvar_train) - 1) * 100
    
    performance = {
        'train': {
            'cvar': cvar_train,
            'var': var_train,
            'mean_return': mean_return_train,
            'volatility': std_train,
            'sharpe_ratio': sharpe_train
        },
        'test': {
            'cvar': cvar_test,
            'var': var_test,
            'mean_return': mean_return_test,
            'volatility': std_test,
            'sharpe_ratio': sharpe_test
        },
        'cvar_deterioration_pct': cvar_deterioration
    }
    
    # Benchmark comparison if provided
    if index_returns_train is not None and index_returns_test is not None:
        cvar_idx_train, var_idx_train = calculate_cvar_index(index_returns_train, beta)
        cvar_idx_test, var_idx_test = calculate_cvar_index(index_returns_test, beta)
        
        performance['benchmark'] = {
            'train': {
                'cvar': cvar_idx_train,
                'var': var_idx_train,
                'mean_return': index_returns_train.mean(),
                'volatility': index_returns_train.std()
            },
            'test': {
                'cvar': cvar_idx_test,
                'var': var_idx_test,
                'mean_return': index_returns_test.mean(),
                'volatility': index_returns_test.std()
            }
        }
        
        # Outperformance
        performance['cvar_outperformance_pct'] = (
            (cvar_idx_test - cvar_test) / cvar_idx_test * 100
        )
    
    return performance


def calculate_cvar_index(returns: pd.Series, beta: float) -> Tuple[float, float]:
    """
    Calculate CVaR for an index (single asset).
    
    Parameters
    ----------
    returns : pd.Series
        Index returns
    beta : float
        Confidence level
        
    Returns
    -------
    cvar_val : float
        Conditional Value-at-Risk
    var_val : float
        Value-at-Risk
    """
    losses = -returns.values
    var_val = np.percentile(losses, beta * 100)
    tail_losses = losses[losses >= var_val]
    cvar_val = np.mean(tail_losses) if len(tail_losses) > 0 else var_val
    
    return cvar_val, var_val


def compare_beta_sensitivity(
    results: Dict[float, Dict]
) -> pd.DataFrame:
    """
    Compare portfolio characteristics across different beta values.
    
    Parameters
    ----------
    results : dict
        Dictionary mapping beta values to optimization results
        Format: {beta: {'weights': array, 'cvar_train': float, ...}}
        
    Returns
    -------
    comparison : pd.DataFrame
        Comparison table
    """
    comparison_data = []
    
    for beta, result in sorted(results.items()):
        weights = result['weights']
        n_positions = np.sum(weights > 1e-6)
        max_weight = np.max(weights)
        top_5_weight = np.sort(weights)[-5:].sum()
        herfindahl = np.sum(weights ** 2)
        
        comparison_data.append({
            'Beta': beta,
            'CVaR_Train': result.get('cvar_train', np.nan),
            'CVaR_Test': result.get('cvar_test', np.nan),
            'CVaR_Deterioration_%': result.get('cvar_deterioration_pct', np.nan),
            'N_Positions': n_positions,
            'Max_Weight': max_weight,
            'Top_5_Concentration': top_5_weight,
            'Herfindahl_Index': herfindahl
        })
    
    return pd.DataFrame(comparison_data)


def analyze_monthly_rebalancing(
    monthly_portfolios: Dict[str, Dict],
    monthly_performance: Dict[str, Dict],
    baseline_performance: Dict
) -> Dict:
    """
    Analyze the effectiveness of monthly rebalancing.
    
    Parameters
    ----------
    monthly_portfolios : dict
        Dictionary of monthly portfolio weights
    monthly_performance : dict
        Dictionary of monthly performance metrics
    baseline_performance : dict
        Performance of static portfolio
        
    Returns
    -------
    analysis : dict
        Summary of rebalancing analysis
    """
    # Extract monthly CVaRs
    monthly_cvars = [perf['cvar_realized'] for perf in monthly_performance.values()]
    
    # Statistics
    avg_cvar = np.mean(monthly_cvars)
    std_cvar = np.std(monthly_cvars)
    min_cvar = np.min(monthly_cvars)
    max_cvar = np.max(monthly_cvars)
    
    # Compare to baseline
    baseline_cvar = baseline_performance['test']['cvar']
    improvement_pct = ((baseline_cvar - avg_cvar) / baseline_cvar) * 100
    
    analysis = {
        'monthly_avg_cvar': avg_cvar,
        'monthly_std_cvar': std_cvar,
        'monthly_min_cvar': min_cvar,
        'monthly_max_cvar': max_cvar,
        'baseline_cvar': baseline_cvar,
        'improvement_pct': improvement_pct,
        'n_months': len(monthly_cvars)
    }
    
    return analysis


def analyze_portfolio_stability(
    monthly_portfolios: Dict[str, Dict],
    max_change_threshold: float = 0.05
) -> Dict:
    """
    Analyze portfolio stability across months.
    
    Parameters
    ----------
    monthly_portfolios : dict
        Dictionary mapping 'YYYY-MM' to portfolio info
    max_change_threshold : float, default=0.05
        Maximum allowed weight change (e.g., 0.05 = 5%)
        
    Returns
    -------
    stability_analysis : dict
        Stability metrics and violations
    """
    months = sorted(monthly_portfolios.keys())
    
    max_changes = []
    violations = []
    unstable_transitions = []
    
    for i in range(len(months) - 1):
        month_curr = months[i]
        month_next = months[i + 1]
        
        weights_curr = monthly_portfolios[month_curr]['weights']
        weights_next = monthly_portfolios[month_next]['weights']
        
        # Calculate maximum absolute change
        weight_changes = np.abs(weights_next - weights_curr)
        max_change = np.max(weight_changes)
        max_changes.append(max_change)
        
        # Check for violations
        if max_change > max_change_threshold:
            violations.append({
                'transition': f"{month_curr} → {month_next}",
                'max_change': max_change,
                'n_violations': np.sum(weight_changes > max_change_threshold)
            })
            unstable_transitions.append(f"{month_curr} → {month_next}")
    
    is_stable = len(violations) == 0
    stability_rate = (1 - len(violations) / len(max_changes)) * 100 if max_changes else 100
    
    stability_analysis = {
        'is_stable': is_stable,
        'stability_rate_pct': stability_rate,
        'max_changes': max_changes,
        'avg_max_change': np.mean(max_changes) if max_changes else 0,
        'violations': violations,
        'n_violations': len(violations),
        'unstable_transitions': unstable_transitions
    }
    
    return stability_analysis


def calculate_turnover(
    weights_old: np.ndarray,
    weights_new: np.ndarray
) -> float:
    """
    Calculate portfolio turnover between two periods.
    
    Turnover is defined as the sum of absolute weight changes divided by 2.
    
    Parameters
    ----------
    weights_old : np.ndarray
        Previous period weights
    weights_new : np.ndarray
        Current period weights
        
    Returns
    -------
    turnover : float
        Portfolio turnover (0 to 1)
    """
    turnover = np.sum(np.abs(weights_new - weights_old)) / 2
    return turnover


def create_performance_summary(
    baseline_perf: Dict,
    minimax_perf: Dict,
    rebalancing_analysis: Dict,
    stability_analysis: Dict
) -> pd.DataFrame:
    """
    Create comprehensive performance summary table.
    
    Parameters
    ----------
    baseline_perf : dict
        Baseline portfolio performance
    minimax_perf : dict
        Minimax portfolio performance
    rebalancing_analysis : dict
        Monthly rebalancing analysis
    stability_analysis : dict
        Portfolio stability analysis
        
    Returns
    -------
    summary : pd.DataFrame
        Performance summary table
    """
    summary_data = []
    
    # Baseline (static portfolio)
    summary_data.append({
        'Strategy': 'Baseline (Static)',
        'Train_CVaR': baseline_perf['train']['cvar'],
        'Test_CVaR': baseline_perf['test']['cvar'],
        'CVaR_Deterioration_%': baseline_perf['cvar_deterioration_pct'],
        'Sharpe_Ratio_Test': baseline_perf['test']['sharpe_ratio']
    })
    
    # Minimax
    if minimax_perf:
        summary_data.append({
            'Strategy': 'Minimax (Worst-Case)',
            'Train_CVaR': minimax_perf['train']['cvar'],
            'Test_CVaR': minimax_perf['test']['cvar'],
            'CVaR_Deterioration_%': minimax_perf['cvar_deterioration_pct'],
            'Sharpe_Ratio_Test': minimax_perf['test']['sharpe_ratio']
        })
    
    # Monthly rebalancing
    if rebalancing_analysis:
        summary_data.append({
            'Strategy': 'Monthly Rebalancing',
            'Train_CVaR': np.nan,  # Not applicable
            'Test_CVaR': rebalancing_analysis['monthly_avg_cvar'],
            'CVaR_Deterioration_%': -rebalancing_analysis['improvement_pct'],
            'Sharpe_Ratio_Test': np.nan
        })
    
    summary = pd.DataFrame(summary_data)
    return summary
