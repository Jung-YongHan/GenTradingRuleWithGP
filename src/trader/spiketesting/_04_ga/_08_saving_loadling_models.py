import numpy as np
from mealpy import GA, FloatVar, Problem
from mealpy.evolutionary_based.GA import BaseGA
from mealpy.utils import io

def objective_function(solution):
        return np.sum(solution**2)

problem = {
    "obj_func": objective_function,
    "bounds": FloatVar(lb=[-100, ] * 50, ub=[100, ] * 50),
    "minmax": "min",
}

## Run the algorithm
model = BaseGA(epoch=100, pop_size=50)
g_best = model.solve(problem)
print(f"Best solution: {g_best.solution}, Best fitness: {g_best.target.fitness}")

## Save model to file
io.save_model(model, "model.pkl")

## Load the model from file
optimizer = io.load_model("model.pkl")
print(f"Best solution: {optimizer.g_best.solution}, Best fitness: {optimizer.g_best.target.fitness}")