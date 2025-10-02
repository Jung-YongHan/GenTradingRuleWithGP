from mealpy import FloatVar, GA
import numpy as np
from mealpy.bio_based import SMA
from mealpy.swarm_based import ABC
from sklearn.model_selection import ParameterGrid

from bt4.utils.stopwatch import StopWatch



def objective_func(solution):
    global num_exec
    return np.sum(solution**2)

# Use max epochs and max function evaluations together
term_dict = {
   # "max_epoch": 200,
   # "max_fe": 100*50 + 50 + 1 # epoch x pop + pop + 1만큼 수행
    "max_fe": 200,
   #  "max_time" : 1
}


problem_dict = {
    "obj_func": objective_func,
    "bounds": FloatVar(lb=[-100, ] * 30, ub=[100, ] * 30,),
    "minmax": "min",
    "log_to"   : "file",
    "log_file" : "result.log",  # Default value = "mealpy.log"
}


sw = StopWatch()
sw.start()


# optimizer = ABC.OriginalABC(epoch = 1000, pop_size = 50, n_limits = 50)
# optimizer = GA.BaseGA(epoch=1000, pop_size=50, pc=0.85, pm=0.1)  ## ABC보다 좋은 성능을 보임

optim_pgm_grid = {
    "epoch"    : [100, 200, 300, 500, 1000],
    "pop_size" : [50, 100],
    # "pc"       : [0.85, 0.90, 0.95],
    # "pm"       : [0.015, 0.025, 0.035]
    "pc"       : [0.85, 0.95],
    "pm"       : [0.015, 0.035]
}

best_fitness = 10000000000
best_solution = ""
for paras_de in list(ParameterGrid(optim_pgm_grid)):
    optimizer = GA.BaseGA(**paras_de)
    optimizer.solve(problem_dict, termination=term_dict)
    # print(optimizer.g_best.solution)
    solution = optimizer.g_best.solution
    fitness = optimizer.g_best.target.fitness
    print(f"executing : {paras_de}")
    if fitness < best_fitness:
        print(f"fitness updated: {best_fitness} => ", end = "")
        best_fitness = fitness
        print(f"{best_fitness}")
        print(f"solution updated: {best_solution} => ", end = "")
        best_solution = solution
        print(f"{best_solution}")
        print(f"ga parameter: {paras_de}")
        print("="*100)








# optimizer.solve(problem_dict)
print(f"Stopwatch: Computing GA =>  {sw.stop()}")


# optimizer = SMA.OriginalSMA(epoch=100, pop_size=50, pr=0.03)
# optimizer.solve(problem_dict)

# optimizer = SMA.OriginalSMA(epoch=100, pop_size=50, pr=0.03)
# optimizer.solve(problem_dict, termination=term_dict)




