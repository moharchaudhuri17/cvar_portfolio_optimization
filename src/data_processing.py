"""
Data Processing Module

Functions for loading, preprocessing, and transforming stock price data
into returns suitable for CVaR optimization.
"""

import pandas as pd
import numpy as np
from pandas.api.types import is_object_dtype
from typing import Tuple, Optional


def load_stock_data(
    filepath_2019: str,
    filepath_2020: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load stock price data from CSV files.
    
    Parameters
    ----------
    filepath_2019 : str
        Path to 2019 stock data CSV
    filepath_2020 : str
        Path to 2020 stock data CSV
        
    Returns
    -------
    stocks_2019 : pd.DataFrame
        2019 stock price data
    stocks_2020 : pd.DataFrame
        2020 stock price data
    """
    stocks_2019 = pd.read_csv(filepath_2019)
    stocks_2020 = pd.read_csv(filepath_2020)
    
    return stocks_2019, stocks_2020


def calculate_returns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate percentage returns from price data.
    
    Parameters
    ----------
    data : pd.DataFrame
        Stock price data
        
    Returns
    -------
    returns : pd.DataFrame
        Percentage returns (first row with NaN dropped)
    """
    price = data.copy()
    
    # Drop first column if it's a date/object column
    if is_object_dtype(price.iloc[:, 0]):
        price = price.drop(price.columns[0], axis=1)
    
    # Calculate percentage returns
    returns = price.pct_change().dropna()
    
    return returns


def separate_index_and_stocks(
    returns: pd.DataFrame,
    index_name: str = 'NDX'
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Separate index returns from stock returns.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Returns data including index
    index_name : str, default='NDX'
        Name of the index column
        
    Returns
    -------
    stock_returns : pd.DataFrame
        Returns for individual stocks (excluding index)
    index_returns : pd.Series
        Returns for the index
    """
    if index_name in returns.columns:
        index_returns = returns[index_name]
        stock_returns = returns.drop(columns=[index_name])
    else:
        print(f"Warning: Index '{index_name}' not found in data")
        index_returns = None
        stock_returns = returns
    
    return stock_returns, index_returns


def load_and_process_data(
    filepath_2019: str = 'data/stocks2019.csv',
    filepath_2020: str = 'data/stocks2020.csv'
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Complete data loading and processing pipeline.
    
    Parameters
    ----------
    filepath_2019 : str
        Path to 2019 stock data
    filepath_2020 : str
        Path to 2020 stock data
        
    Returns
    -------
    stock_returns_2019 : pd.DataFrame
        2019 stock returns
    stock_returns_2020 : pd.DataFrame
        2020 stock returns
    ndx_returns_2019 : pd.Series
        2019 NDX index returns
    ndx_returns_2020 : pd.Series
        2020 NDX index returns
    """
    # Load data
    print("Loading stock data...")
    stocks_2019, stocks_2020 = load_stock_data(filepath_2019, filepath_2020)
    print(f"2019 data shape: {stocks_2019.shape}")
    print(f"2020 data shape: {stocks_2020.shape}")
    
    # Calculate returns
    print("\nCalculating returns...")
    returns_2019 = calculate_returns(stocks_2019)
    returns_2020 = calculate_returns(stocks_2020)
    print(f"2019 returns shape: {returns_2019.shape}")
    print(f"2020 returns shape: {returns_2020.shape}")
    
    # Separate stocks and index
    print("\nSeparating stocks from index...")
    stock_returns_2019, ndx_returns_2019 = separate_index_and_stocks(returns_2019)
    stock_returns_2020, ndx_returns_2020 = separate_index_and_stocks(returns_2020)
    print(f"Number of stocks: {len(stock_returns_2019.columns)}")
    
    return stock_returns_2019, stock_returns_2020, ndx_returns_2019, ndx_returns_2020


def get_rolling_window_data(
    stocks_2019: pd.DataFrame,
    stocks_2020: pd.DataFrame,
    target_month: str
) -> pd.DataFrame:
    """
    Get 12-month rolling window of returns data for a target month.
    
    For example, to optimize for January 2020, we use data from
    January 2019 through December 2019.
    
    Parameters
    ----------
    stocks_2019 : pd.DataFrame
        2019 stock price data
    stocks_2020 : pd.DataFrame
        2020 stock price data
    target_month : str
        Target month in format 'YYYY-MM' (e.g., '2020-01')
        
    Returns
    -------
    window_returns : pd.DataFrame
        12 months of returns data preceding target month
    """
    year, month = map(int, target_month.split('-'))
    
    if year != 2020:
        raise ValueError("Only 2020 target months are supported")
    
    # Combine 2019 and 2020 data
    combined = pd.concat([stocks_2019, stocks_2020], ignore_index=True)
    
    # Calculate returns for combined data
    returns = calculate_returns(combined)
    
    # Get 12-month window ending just before target month
    # For Jan 2020 (month 1), we want Jan 2019 - Dec 2019
    # For Feb 2020 (month 2), we want Feb 2019 - Jan 2020, etc.
    
    # This is a simplified version - in practice you'd need to handle dates properly
    # Assuming daily data with ~250 trading days per year
    days_per_month = 21
    end_idx = (month - 1) * days_per_month + 250  # 250 days for all of 2019
    start_idx = end_idx - 250  # 12 months of data
    
    window_returns = returns.iloc[start_idx:end_idx]
    
    return window_returns


def summarize_portfolio(
    weights: np.ndarray,
    stock_names: list,
    returns: pd.DataFrame,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Create a summary DataFrame of portfolio holdings.
    
    Parameters
    ----------
    weights : np.ndarray
        Portfolio weights
    stock_names : list
        Names of stocks
    returns : pd.DataFrame
        Returns data for calculating statistics
    top_n : int, default=10
        Number of top holdings to highlight
        
    Returns
    -------
    summary : pd.DataFrame
        Portfolio summary with weights and returns
    """
    mean_returns = returns.mean().values
    
    portfolio_df = pd.DataFrame({
        'Stock': stock_names,
        'Weight': weights,
        'Mean_Return': mean_returns,
        'Contribution': weights * mean_returns
    })
    
    # Sort by weight
    portfolio_df = portfolio_df.sort_values('Weight', ascending=False)
    
    # Add rank
    portfolio_df['Rank'] = range(1, len(portfolio_df) + 1)
    
    # Filter to show only positions > 0.01%
    portfolio_df = portfolio_df[portfolio_df['Weight'] > 0.0001].reset_index(drop=True)
    
    return portfolio_df


def calculate_portfolio_statistics(
    weights: np.ndarray,
    returns: pd.DataFrame
) -> dict:
    """
    Calculate key portfolio statistics.
    
    Parameters
    ----------
    weights : np.ndarray
        Portfolio weights
    returns : pd.DataFrame
        Returns data
        
    Returns
    -------
    stats : dict
        Dictionary of portfolio statistics
    """
    # Returns
    mean_returns = returns.mean().values
    portfolio_return = np.dot(weights, mean_returns)
    
    # Risk
    cov_matrix = returns.cov().values
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    portfolio_std = np.sqrt(portfolio_variance)
    
    # Sharpe ratio (assuming 0 risk-free rate)
    sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0
    
    # Concentration
    n_positions = np.sum(weights > 1e-6)
    max_weight = np.max(weights)
    herfindahl = np.sum(weights ** 2)
    
    stats = {
        'expected_return': portfolio_return,
        'volatility': portfolio_std,
        'sharpe_ratio': sharpe_ratio,
        'n_positions': n_positions,
        'max_weight': max_weight,
        'herfindahl_index': herfindahl
    }
    
    return stats
