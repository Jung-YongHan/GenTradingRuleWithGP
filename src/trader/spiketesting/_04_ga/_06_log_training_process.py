from mealpy import FloatVar
from mealpy.evolutionary_based import GA
import numpy as np

# problem_dict1 = {
#    "obj_func": F5,
#    "bounds": FloatVar(lb=[-3, -5, 1, -10, ], ub=[5, 10, 100, 30, ]),
#    "minmax": "min",
#    # Default = "console"
# }

# problem_dict1 = {
#    "obj_func": F5,
#    "bounds": FloatVar(lb=[-3, -5, 1, -10, ], ub=[5, 10, 100, 30, ]),
#    "minmax": "min",
#    "log_to": "console",
# }

# problem_dict2 = {
#    "obj_func": F5,
#    "bounds": FloatVar(lb=[-3, -5, 1, -10, ], ub=[5, 10, 100, 30, ]),
#    "minmax": "min",
#    "log_to": "file",
#    "log_file": "result.log",         # Default value = "mealpy.log"
# }

# problem_dict3 = {
#    "obj_func": F5,
#    "bounds": FloatVar(lb=[-3, -5, 1, -10, ], ub=[5, 10, 100, 30, ]),
#    "minmax": "min",
#    "log_to": None,
# }

def objective_func(solution):
    return np.sum(solution**2)

problem_dict = {
    "obj_func": objective_func,
    "bounds": FloatVar(lb=[-100, ] * 30, ub=[100, ] * 30,),
    "minmax": "min",
    "log_to": "file",
    "log_file": "result.log",         # Default value = "mealpy.log"
}

optimizer = GA.BaseGA(epoch=100, pop_size=50, pc=0.85, pm=0.1)
optimizer.solve(problem_dict)

print(optimizer.g_best.solution)
print(optimizer.g_best.target.fitness)

