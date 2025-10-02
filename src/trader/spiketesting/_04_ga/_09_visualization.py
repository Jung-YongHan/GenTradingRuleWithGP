
import numpy as np
from mealpy import FloatVar
from mealpy.bio_based import SMA


def objective_function(solution) :
    return np.sum(solution ** 2)


problem = {
    "obj_func" : objective_function,
    "bounds"   : FloatVar(lb = [-100, ] * 50, ub = [100, ] * 50),
    "minmax"   : "min",
}

model = SMA.OriginalSMA(epoch=100, pop_size=50, pr=0.03)
model.solve(problem)

## You can access them all via object "history" like this:
model.history.save_global_objectives_chart(filename="vis/goc")
model.history.save_local_objectives_chart(filename="vis/loc")

model.history.save_global_best_fitness_chart(filename="vis/gbfc")
model.history.save_local_best_fitness_chart(filename="vis/lbfc")

model.history.save_runtime_chart(filename="hello/rtc")

model.history.save_exploration_exploitation_chart(filename="vis/eec")

model.history.save_diversity_chart(filename="hello/dc")

model.history.save_trajectory_chart(list_agent_idx=[3, 5, 6, 7,], selected_dimensions=[3, 4], filename="vis/tc")