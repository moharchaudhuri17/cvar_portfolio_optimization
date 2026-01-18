"""
CVaR Portfolio Optimization Package

A comprehensive toolkit for portfolio optimization using Conditional Value-at-Risk.
"""

from .cvar_optimizer import (
    solve_cvar_portfolio,
    solve_cvar_minimax,
    solve_cvar_with_stability,
    calculate_cvar
)

from .data_processing import (
    load_and_process_data,
    calculate_returns,
    summarize_portfolio,
    calculate_portfolio_statistics
)

from .analysis import (
    evaluate_portfolio_performance,
    compare_beta_sensitivity,
    analyze_monthly_rebalancing,
    analyze_portfolio_stability
)

from .visualization import (
    plot_portfolio_weights,
    plot_beta_comparison,
    plot_monthly_cvar_evolution,
    plot_stability_analysis,
    plot_cumulative_returns
)

__version__ = "1.0.0"
__author__ = "Momo"

__all__ = [
    # Optimization
    'solve_cvar_portfolio',
    'solve_cvar_minimax',
    'solve_cvar_with_stability',
    'calculate_cvar',
    # Data processing
    'load_and_process_data',
    'calculate_returns',
    'summarize_portfolio',
    'calculate_portfolio_statistics',
    # Analysis
    'evaluate_portfolio_performance',
    'compare_beta_sensitivity',
    'analyze_monthly_rebalancing',
    'analyze_portfolio_stability',
    # Visualization
    'plot_portfolio_weights',
    'plot_beta_comparison',
    'plot_monthly_cvar_evolution',
    'plot_stability_analysis',
    'plot_cumulative_returns',
]
