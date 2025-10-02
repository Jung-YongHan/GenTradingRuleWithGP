import numpy as np
from mealpy import PSO, FloatVar, Problem

## This is how you design multi-objective function
#### Link: https://en.wikipedia.org/wiki/Test_functions_for_optimization
def objective_multi(solution):
    def booth(x, y):
        return (x + 2*y - 7)**2 + (2*x + y - 5)**2
    def bukin(x, y):
        return 100 * np.sqrt(np.abs(y - 0.01 * x**2)) + 0.01 * np.abs(x + 10)
    def matyas(x, y):
        return 0.26 * (x**2 + y**2) - 0.48 * x * y
    return [booth(solution[0], solution[1]), bukin(solution[0], solution[1]), matyas(solution[0], solution[1])]

## Design a problem dictionary for multiple objective functions above
problem_multi = {
    "obj_func": objective_multi,
    "bounds": FloatVar(lb=[-10, -10], ub=[10, 10]),
    "minmax": "min",
    "obj_weights": [0.4, 0.1, 0.5]               # Define it or default value will be [1, 1, 1]
}

## Define the model and solve the problem
model = PSO.OriginalPSO(epoch=1000, pop_size=50)
model.solve(problem=problem_multi)