import numpy as np
from mealpy import PSO, FloatVar
from mealpy.utils.problem import Problem


## Define a custom child class of Problem class.
class COP(Problem):
    def __init__(self, bounds, minmax, name="COP", **kwargs):
        self.name = name
        super().__init__(bounds, minmax, **kwargs)

    def g1(self, x):
        return 2 * x[0] + 2 * x[1] + x[9] + x[10] - 10
    def g2(self, x):
        return 2 * x[0] + 2 * x[2] + x[9] + x[10] - 10
    def g3(self, x):
        return 2 * x[1] + 2 * x[2] + x[10] + x[11] - 10
    def g4(self, x):
        return -8 * x[0] + x[9]
    def g5(self, x):
        return -8 * x[1] + x[10]
    def g6(self, x):
        return -8 * x[2] + x[11]
    def g7(self, x):
        return -2 * x[3] - x[4] + x[9]
    def g8(self, x):
        return -2 * x[5] - x[6] + x[10]
    def g9(self, x):
        return -2 * x[7] - x[8] + x[11]

    def violate(self, value):
        return 0 if value <= 0 else value

    def obj_func(self, solution):
        ## This is how you design Constrained Benchmark Function (G01)
        #### Link: https://onlinelibrary.wiley.com/doi/pdf/10.1002/9781119136507.app2

        fx = 5 * np.sum(solution[:4]) - 5 * np.sum(solution[:4] ** 2) - np.sum(solution[4:13])

        ## Increase the punishment for g1 and g4 to boost the algorithm (You can choice any constraint instead of g1 and g4)
        fx += self.violate(self.g1(solution)) ** 2 + self.violate(self.g2(solution)) + self.violate(self.g3(solution)) + \
            2 * self.violate(self.g4(solution)) + self.violate(self.g5(solution)) + self.violate(self.g6(solution)) + \
            self.violate(self.g7(solution)) + self.violate(self.g8(solution)) + self.violate(self.g9(solution))

        return fx

## Create an instance of MOP class
bounds = FloatVar(lb=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], ub=[1, 1, 1, 1, 1, 1, 1, 1, 1, 100, 100, 100, 1]),
problem_cop = COP(bounds=bounds, minmax="min")

## Define the model and solve the problem
optimizer = PSO.OriginalPSO(epoch=1000, pop_size=50)
optimizer.solve(problem=problem_cop)

print(optimizer.g_best.solution)
print(optimizer.g_best.target.fitness)
