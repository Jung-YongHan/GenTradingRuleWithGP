import numpy as np
from mealpy import PSO, FloatVar, Problem

## Define a custom child class of Problem class.
class MOP(Problem):
    def __init__(self, bounds=None, minmax="min", name="MOP", **kwargs):
        self.name = name
        self.exec_nums = 0
        super().__init__(bounds, minmax, **kwargs)

    def booth(self, x, y):
        self.exec_nums += 1
        print(f"exec: {self.exec_nums}")
        return (x + 2*y - 7)**2 + (2*x + y - 5)**2
    def bukin(self, x, y):
        return 100 * np.sqrt(np.abs(y - 0.01 * x**2)) + 0.01 * np.abs(x + 10)
    def matyas(self, x, y):
        return 0.26 * (x**2 + y**2) - 0.48 * x * y

    def obj_func(self, solution):
        return [self.booth(solution[0], solution[1]), self.bukin(solution[0], solution[1]), self.matyas(solution[0], solution[1])]

## Create an instance of MOP class
problem_multi = MOP(bounds=FloatVar(lb=[-10, ] * 2, ub=[10, ] * 2), minmax="min", obj_weights=[0.4, 0.1, 0.5])

term_dict = {
   #  "max_fe": 200,
    "max_early_stop": 100
}

# 100*50 + 50 + 1= 5051번 이상에서 멈춤 예상 => (실제) 12451회에서 멈춤,  fitness = 7.343046331627907

## Define the model and solve the problem
optimizer = PSO.OriginalPSO(epoch=1000, pop_size=50)
optimizer.solve(problem=problem_multi, termination = term_dict)

print(optimizer.g_best.solution)
print(optimizer.g_best.target.fitness)
