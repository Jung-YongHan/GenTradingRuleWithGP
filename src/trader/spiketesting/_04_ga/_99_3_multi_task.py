#### Using multiple algorithm to solve multiple problems with multiple trials

## Import libraries
## For example, we want to solve F5, F10, F29 problem in CEC-2017
from opfunu.cec_based.cec2017 import F52017, F102017, F292017

from mealpy.bio_based import BBO
from mealpy.evolutionary_based import DE
from mealpy.multitask import Multitask  # Remember this

## You can define your own problems

f1 = F52017(30, f_bias=0)
f2 = F102017(30, f_bias=0)
f3 = F292017(30, f_bias=0)

p1 = {
    "lb": f1.lb.tolist(),
    "ub": f1.ub.tolist(),
    "minmax": "min",
    "fit_func": f1.evaluate,
    "name": "F5-CEC2017",
    "log_to": None,
}

p2 = {
    "lb": f2.lb.tolist(),
    "ub": f2.ub.tolist(),
    "minmax": "min",
    "fit_func": f2.evaluate,
    "name": "F10-CEC2017",
    "log_to": None,
}

p3 = {
    "lb": f3.lb.tolist(),
    "ub": f3.ub.tolist(),
    "minmax": "min",
    "fit_func": f3.evaluate,
    "name": "F29-CEC2017",
    "log_to": None,
}

## Define models


# model1 = BBO.BaseBBO(epoch=10, pop_size=50)
# model2 = BBO.OriginalBBO(epoch=10, pop_size=50)
# model3 = DE.BaseDE(epoch=10, pop_size=50)

model1 = BBO.OriginalBBO(epoch=10, pop_size=50)
model2 = BBO.DevBBO(epoch=10, pop_size=50)
model3 = DE.SADE(epoch=10, pop_size=50)


## Define and run Multitask

if __name__ == "__main__":
    multitask = Multitask(algorithms=(model1, model2, model3), problems=(p1, p2, p3))
    multitask.execute(n_trials=3, mode="parallel", n_workers=6, save_path="history", save_as="csv",
                      save_convergence=True, verbose=True)

    ## Check the directory: history/, you will see list of .csv result files