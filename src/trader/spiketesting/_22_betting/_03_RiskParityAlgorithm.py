import numpy as np
from scipy.optimize import minimize

# Data
volatility = np.array([0.035, 0.042, 0.054])
correlation = np.array([[1, 0.8, 0.4],
                        [0.8, 1, 0.5],
                        [0.4, 0.5, 1]])

# Covariance matrix
cov_matrix = np.outer(volatility, volatility) * correlation

# Objective function: Minimize variance contribution differences
def objective(weights):
    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    risk_contributions = weights * np.dot(cov_matrix, weights) / portfolio_vol
    return np.std(risk_contributions)

# Constraints: weights sum to 1
constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

# Bounds: weights are between 0 and 1
bounds = [(0, 1) for _ in range(3)]

# Initial guess
initial_weights = np.array([1/3, 1/3, 1/3])

# Solve optimization
result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

# Optimal weights
optimal_weights = result.x
print("Optimal Weights:", optimal_weights)