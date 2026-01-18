"""
Unit tests for CVaR optimizer module
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from cvar_optimizer import solve_cvar_portfolio, calculate_cvar


class TestCVaROptimizer:
    """Test suite for CVaR optimization functions"""
    
    @pytest.fixture
    def sample_returns(self):
        """Create sample returns data for testing"""
        np.random.seed(42)
        n_days = 100
        n_stocks = 10
        
        # Generate random returns
        returns = np.random.randn(n_days, n_stocks) * 0.02 + 0.001
        
        stock_names = [f"STOCK{i}" for i in range(n_stocks)]
        returns_df = pd.DataFrame(returns, columns=stock_names)
        
        return returns_df
    
    def test_solve_cvar_portfolio_basic(self, sample_returns):
        """Test basic CVaR optimization"""
        weights, alpha, model = solve_cvar_portfolio(
            returns_data=sample_returns,
            beta=0.95,
            R_target=0.0001,
            verbose=False
        )
        
        # Check weights sum to 1
        assert np.isclose(weights.sum(), 1.0, atol=1e-6), "Weights should sum to 1"
        
        # Check all weights are non-negative
        assert np.all(weights >= -1e-6), "All weights should be non-negative"
        
        # Check CVaR is positive
        assert model.ObjVal > 0, "CVaR should be positive"
        
        # Check dimensions
        assert len(weights) == len(sample_returns.columns), "Weight vector size mismatch"
    
    def test_solve_cvar_portfolio_different_betas(self, sample_returns):
        """Test optimization with different beta values"""
        betas = [0.90, 0.95, 0.99]
        cvars = []
        
        for beta in betas:
            weights, alpha, model = solve_cvar_portfolio(
                returns_data=sample_returns,
                beta=beta,
                R_target=0.0001,
                verbose=False
            )
            cvars.append(model.ObjVal)
        
        # CVaR should generally increase with beta
        # (higher confidence level = worse tail losses)
        assert cvars[1] > cvars[0] or np.isclose(cvars[1], cvars[0], rtol=0.1)
        assert cvars[2] > cvars[1] or np.isclose(cvars[2], cvars[1], rtol=0.1)
    
    def test_calculate_cvar_function(self, sample_returns):
        """Test CVaR calculation function"""
        # Create equal-weight portfolio
        n_stocks = len(sample_returns.columns)
        weights = np.ones(n_stocks) / n_stocks
        
        cvar, var = calculate_cvar(sample_returns, weights, beta=0.95)
        
        # Basic sanity checks
        assert cvar > 0, "CVaR should be positive"
        assert var > 0, "VaR should be positive"
        assert cvar >= var, "CVaR should be >= VaR"
    
    def test_minimum_return_constraint(self, sample_returns):
        """Test that minimum return constraint is satisfied"""
        R_target = 0.0005
        
        weights, alpha, model = solve_cvar_portfolio(
            returns_data=sample_returns,
            beta=0.95,
            R_target=R_target,
            verbose=False
        )
        
        mean_returns = sample_returns.mean().values
        portfolio_return = np.dot(weights, mean_returns)
        
        assert portfolio_return >= R_target - 1e-6, \
            f"Portfolio return {portfolio_return} should be >= {R_target}"
    
    def test_no_short_selling_constraint(self, sample_returns):
        """Test that no-short-selling constraint is enforced"""
        weights, alpha, model = solve_cvar_portfolio(
            returns_data=sample_returns,
            beta=0.95,
            R_target=0.0001,
            verbose=False
        )
        
        # All weights should be non-negative
        assert np.all(weights >= -1e-6), \
            f"Found negative weight: {weights.min()}"
    
    def test_cvar_with_extreme_beta(self, sample_returns):
        """Test behavior with extreme beta values"""
        # Test with very conservative beta
        weights_conservative, _, model_conservative = solve_cvar_portfolio(
            returns_data=sample_returns,
            beta=0.99,
            R_target=0.0001,
            verbose=False
        )
        
        # Test with less conservative beta
        weights_normal, _, model_normal = solve_cvar_portfolio(
            returns_data=sample_returns,
            beta=0.90,
            R_target=0.0001,
            verbose=False
        )
        
        # Both should produce valid portfolios
        assert np.isclose(weights_conservative.sum(), 1.0, atol=1e-6)
        assert np.isclose(weights_normal.sum(), 1.0, atol=1e-6)
    
    def test_infeasible_problem(self, sample_returns):
        """Test handling of infeasible optimization problem"""
        # Set impossibly high return requirement
        R_target = 1.0  # 100% daily return - clearly infeasible
        
        # This should either raise an exception or return a status != OPTIMAL
        with pytest.warns(UserWarning) or pytest.raises(Exception):
            weights, alpha, model = solve_cvar_portfolio(
                returns_data=sample_returns,
                beta=0.95,
                R_target=R_target,
                verbose=False
            )


class TestCVaRCalculation:
    """Test suite for CVaR calculation functions"""
    
    def test_cvar_equals_var_for_deterministic_loss(self):
        """Test that CVaR equals VaR for deterministic outcomes"""
        # Create returns where all scenarios have the same loss
        n_days = 100
        returns = pd.DataFrame({
            'STOCK1': [-0.02] * n_days,  # Constant 2% loss
        })
        weights = np.array([1.0])
        
        cvar, var = calculate_cvar(returns, weights, beta=0.95)
        
        # For deterministic loss, CVaR should equal VaR
        assert np.isclose(cvar, var, rtol=0.01), \
            f"CVaR {cvar} should equal VaR {var} for deterministic loss"
    
    def test_cvar_calculation_consistency(self):
        """Test that CVaR calculation is consistent"""
        np.random.seed(123)
        returns = pd.DataFrame({
            'STOCK1': np.random.randn(200) * 0.02,
            'STOCK2': np.random.randn(200) * 0.02
        })
        weights = np.array([0.6, 0.4])
        
        # Calculate CVaR multiple times
        cvar1, var1 = calculate_cvar(returns, weights, beta=0.95)
        cvar2, var2 = calculate_cvar(returns, weights, beta=0.95)
        
        # Should get same results
        assert np.isclose(cvar1, cvar2, rtol=1e-10)
        assert np.isclose(var1, var2, rtol=1e-10)


class TestPortfolioConstraints:
    """Test portfolio constraint satisfaction"""
    
    @pytest.fixture
    def test_returns(self):
        """Generate test returns"""
        np.random.seed(456)
        return pd.DataFrame({
            f'STOCK{i}': np.random.randn(150) * 0.015 + 0.0005
            for i in range(20)
        })
    
    def test_full_investment_constraint(self, test_returns):
        """Verify full investment constraint"""
        for beta in [0.90, 0.95, 0.99]:
            weights, _, _ = solve_cvar_portfolio(
                test_returns, beta, R_target=0.0002, verbose=False
            )
            assert np.isclose(weights.sum(), 1.0, atol=1e-5), \
                f"Weights sum to {weights.sum()}, expected 1.0 for beta={beta}"
    
    def test_non_negativity_constraint(self, test_returns):
        """Verify non-negativity of weights"""
        weights, _, _ = solve_cvar_portfolio(
            test_returns, beta=0.95, R_target=0.0002, verbose=False
        )
        assert np.all(weights >= -1e-6), \
            f"Negative weights found: min={weights.min()}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
