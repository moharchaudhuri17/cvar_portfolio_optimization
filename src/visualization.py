"""
Visualization Module

Functions for creating plots and visualizations of portfolio optimization results.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def plot_portfolio_weights(
    weights: np.ndarray,
    stock_names: List[str],
    title: str = "Portfolio Allocation",
    top_n: int = 15,
    figsize: tuple = (12, 6)
) -> plt.Figure:
    """
    Plot bar chart of portfolio weights.
    
    Parameters
    ----------
    weights : np.ndarray
        Portfolio weights
    stock_names : list
        Stock names
    title : str
        Plot title
    top_n : int, default=15
        Number of top holdings to show
    figsize : tuple, default=(12, 6)
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    """
    # Create DataFrame and sort
    portfolio_df = pd.DataFrame({
        'Stock': stock_names,
        'Weight': weights
    }).sort_values('Weight', ascending=False)
    
    # Keep only top N and non-zero
    portfolio_df = portfolio_df[portfolio_df['Weight'] > 1e-6].head(top_n)
    
    # Plot
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(range(len(portfolio_df)), portfolio_df['Weight'], 
                   color='steelblue', edgecolor='navy', alpha=0.8)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, portfolio_df['Weight'])):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{value:.1%}', ha='center', va='bottom', fontsize=9)
    
    ax.set_xticks(range(len(portfolio_df)))
    ax.set_xticklabels(portfolio_df['Stock'], rotation=45, ha='right')
    ax.set_ylabel('Portfolio Weight')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    
    plt.tight_layout()
    return fig


def plot_beta_comparison(
    beta_results: Dict[float, Dict],
    figsize: tuple = (14, 10)
) -> plt.Figure:
    """
    Create comprehensive comparison plots for different beta values.
    
    Parameters
    ----------
    beta_results : dict
        Dictionary mapping beta to results
    figsize : tuple, default=(14, 10)
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    betas = sorted(beta_results.keys())
    
    # Extract metrics
    cvars_train = [beta_results[b]['cvar_train'] for b in betas]
    cvars_test = [beta_results[b]['cvar_test'] for b in betas]
    n_positions = [np.sum(beta_results[b]['weights'] > 1e-6) for b in betas]
    max_weights = [np.max(beta_results[b]['weights']) for b in betas]
    
    # Plot 1: CVaR by Beta
    ax1 = axes[0, 0]
    ax1.plot(betas, cvars_train, marker='o', label='In-Sample (2019)', 
             linewidth=2, markersize=8)
    ax1.plot(betas, cvars_test, marker='s', label='Out-of-Sample (2020)', 
             linewidth=2, markersize=8)
    ax1.set_xlabel('Beta (Confidence Level)')
    ax1.set_ylabel('CVaR')
    ax1.set_title('CVaR vs Beta Level', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Number of Positions
    ax2 = axes[0, 1]
    ax2.bar(range(len(betas)), n_positions, color='coral', alpha=0.7, edgecolor='darkred')
    ax2.set_xticks(range(len(betas)))
    ax2.set_xticklabels([f'{b:.2f}' for b in betas])
    ax2.set_xlabel('Beta')
    ax2.set_ylabel('Number of Positions')
    ax2.set_title('Portfolio Diversification', fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Maximum Weight
    ax3 = axes[1, 0]
    ax3.bar(range(len(betas)), max_weights, color='lightgreen', alpha=0.7, edgecolor='darkgreen')
    ax3.set_xticks(range(len(betas)))
    ax3.set_xticklabels([f'{b:.2f}' for b in betas])
    ax3.set_xlabel('Beta')
    ax3.set_ylabel('Maximum Weight')
    ax3.set_title('Maximum Single Position', fontweight='bold')
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Plot 4: CVaR Deterioration
    ax4 = axes[1, 1]
    deteriorations = [((beta_results[b]['cvar_test'] / beta_results[b]['cvar_train']) - 1) * 100 
                      for b in betas]
    colors = ['red' if d > 200 else 'orange' if d > 100 else 'yellow' for d in deteriorations]
    ax4.bar(range(len(betas)), deteriorations, color=colors, alpha=0.7, edgecolor='black')
    ax4.set_xticks(range(len(betas)))
    ax4.set_xticklabels([f'{b:.2f}' for b in betas])
    ax4.set_xlabel('Beta')
    ax4.set_ylabel('CVaR Deterioration (%)')
    ax4.set_title('Out-of-Sample Performance Degradation', fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.axhline(y=0, color='black', linestyle='--', linewidth=1)
    
    plt.suptitle('Beta Sensitivity Analysis', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    return fig


def plot_monthly_cvar_evolution(
    monthly_performance: Dict[str, Dict],
    baseline_cvar: Optional[float] = None,
    figsize: tuple = (14, 6)
) -> plt.Figure:
    """
    Plot evolution of CVaR across months.
    
    Parameters
    ----------
    monthly_performance : dict
        Dictionary of monthly performance metrics
    baseline_cvar : float, optional
        Static portfolio CVaR for comparison
    figsize : tuple, default=(14, 6)
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    """
    months = sorted(monthly_performance.keys())
    cvars = [monthly_performance[m]['cvar_realized'] for m in months]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot monthly CVaR
    ax.plot(range(len(months)), cvars, marker='o', linewidth=2, 
            markersize=8, label='Monthly Rebalanced CVaR', color='steelblue')
    
    # Add baseline if provided
    if baseline_cvar is not None:
        ax.axhline(y=baseline_cvar, color='red', linestyle='--', 
                   linewidth=2, label='Static Portfolio CVaR')
    
    # Formatting
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels([m.split('-')[1] for m in months], rotation=0)
    ax.set_xlabel('Month (2020)', fontsize=12)
    ax.set_ylabel('CVaR', fontsize=12)
    ax.set_title('Monthly CVaR Evolution with Rebalancing', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Add statistics box
    avg_cvar = np.mean(cvars)
    std_cvar = np.std(cvars)
    min_cvar = np.min(cvars)
    max_cvar = np.max(cvars)
    
    stats_text = f'Mean: {avg_cvar:.4f}\nStd: {std_cvar:.4f}\nMin: {min_cvar:.4f}\nMax: {max_cvar:.4f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            fontsize=10)
    
    plt.tight_layout()
    return fig


def plot_stability_analysis(
    stability_results: Dict,
    monthly_performance: Dict[str, Dict],
    stable_performance: Optional[Dict[str, Dict]] = None,
    figsize: tuple = (16, 6)
) -> plt.Figure:
    """
    Plot portfolio stability analysis.
    
    Parameters
    ----------
    stability_results : dict
        Results from stability analysis
    monthly_performance : dict
        Unconstrained monthly performance
    stable_performance : dict, optional
        Performance with stability constraints
    figsize : tuple, default=(16, 6)
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Left: Stability violations
    max_changes = stability_results['max_changes']
    months = sorted(monthly_performance.keys())[:-1]  # One less than performance
    
    colors = ['red' if x > 0.05 else 'green' for x in max_changes]
    bars = ax1.bar(range(len(max_changes)), max_changes, color=colors, 
                   alpha=0.7, edgecolor='black', linewidth=1)
    ax1.axhline(y=0.05, color='red', linestyle='--', linewidth=2, 
                label='5% Stability Threshold')
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, max_changes)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{value:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax1.set_xticks(range(len(months)))
    ax1.set_xticklabels([m[5:] for m in months], rotation=45)
    ax1.set_ylabel('Maximum Weight Change', fontsize=12)
    ax1.set_title('Portfolio Stability: Maximum Monthly Weight Changes', 
                  fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add stability rate
    stability_rate = stability_results['stability_rate_pct']
    ax1.text(0.50, 0.85, f'Stability Rate: {stability_rate:.1f}%',
             transform=ax1.transAxes, fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Right: CVaR comparison
    if stable_performance:
        months_sorted = sorted(monthly_performance.keys())
        unconstrained_cvars = [monthly_performance[m]['cvar_realized'] for m in months_sorted]
        
        stable_months = sorted(stable_performance.keys())
        stable_cvars = [stable_performance[m]['cvar_realized'] for m in stable_months]
        
        # Align datasets
        if len(stable_months) < len(months_sorted):
            months_sorted = stable_months
            unconstrained_cvars = [monthly_performance[m]['cvar_realized'] for m in stable_months]
        
        x_pos = np.arange(len(months_sorted))
        width = 0.35
        
        ax2.bar(x_pos - width/2, unconstrained_cvars, width, 
                label='Unconstrained', alpha=0.8, color='steelblue', edgecolor='navy')
        ax2.bar(x_pos + width/2, stable_cvars, width, 
                label='Stability Constrained', alpha=0.8, color='orange', edgecolor='darkorange')
        
        ax2.set_xlabel('Month', fontsize=12)
        ax2.set_ylabel('CVaR', fontsize=12)
        ax2.set_title('CVaR Performance: Unconstrained vs Stable', 
                      fontsize=14, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([f"{int(m.split('-')[1]):02d}" for m in months_sorted])
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add stats
        unconstrained_avg = np.mean(unconstrained_cvars)
        stable_avg = np.mean(stable_cvars)
        ax2.text(0.50, 0.85, 
                 f'Avg CVaR (Unconstrained): {unconstrained_avg:.6f}\n'
                 f'Avg CVaR (Stable): {stable_avg:.6f}',
                 transform=ax2.transAxes, fontsize=11, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    return fig


def plot_cumulative_returns(
    returns_dict: Dict[str, np.ndarray],
    labels: List[str],
    title: str = "Cumulative Returns Comparison",
    figsize: tuple = (14, 6)
) -> plt.Figure:
    """
    Plot cumulative returns for multiple strategies.
    
    Parameters
    ----------
    returns_dict : dict
        Dictionary mapping strategy names to return arrays
    labels : list
        Labels for plot legend
    title : str
        Plot title
    figsize : tuple, default=(14, 6)
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = ['steelblue', 'coral', 'green', 'purple', 'orange']
    
    for i, (strategy, returns) in enumerate(returns_dict.items()):
        cumulative = (1 + returns).cumprod()
        ax.plot(cumulative, label=labels[i], linewidth=2, 
                color=colors[i % len(colors)])
    
    ax.set_xlabel('Trading Day', fontsize=12)
    ax.set_ylabel('Cumulative Return (Indexed to 1)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=1, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    return fig


def create_summary_table_plot(
    summary_df: pd.DataFrame,
    title: str = "Performance Summary",
    figsize: tuple = (12, 4)
) -> plt.Figure:
    """
    Create a formatted table visualization of summary statistics.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary statistics DataFrame
    title : str
        Table title
    figsize : tuple, default=(12, 4)
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=summary_df.values,
                     colLabels=summary_df.columns,
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header
    for i in range(len(summary_df.columns)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(summary_df) + 1):
        for j in range(len(summary_df.columns)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#E7E6E6')
    
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    
    return fig
