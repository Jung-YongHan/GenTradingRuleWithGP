import numpy as np
from mealpy.bio_based import BBO
from mealpy.utils.problem import Problem

# Our custom problem class
class Squared(Problem):
    def __init__(self, lb=(-5, -5, -5, -5, -5, -5),
                 ub=(5, 5, 5, 5, 5, 5),
                 minmax="min",
                 name="Squared", **kwargs):
        super().__init__(lb, ub, minmax, **kwargs)
        self.name = name

    def fit_func(self, solution):
        return np.sum(solution ** 2)

if __name__ == '__main__':
    problem = Squared(lb=[-10] * 20, ub=[10] * 20, minmax="min")
    model = BBO.BaseBBO(epoch=10, pop_size=50)
    best_position, best_fitness = model.solve(problem)

    print(best_position)
    print(best_fitness)
    print(model.get_parameters())
    print(model.get_name())
    print(model.get_attributes()["solution"])
    print(model.problem.get_name())
    print(model.problem.n_dims)