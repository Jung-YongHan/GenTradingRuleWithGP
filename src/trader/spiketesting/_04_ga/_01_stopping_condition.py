from mealpy import FloatVar, GA
import numpy as np
from mealpy.bio_based import SMA
from mealpy.swarm_based import ABC

from bt4.utils.stopwatch import StopWatch

num_exec = 0


def objective_func(solution):
    global num_exec
    num_exec += 1
    print(f"execution #{num_exec}")
    return np.sum(solution**2)

# Use max epochs and max function evaluations together
term_dict = {
   # "max_epoch": 200,
   # "max_fe": 100*50 + 50 + 1 # epoch x pop + pop + 1만큼 수행
   #  "max_fe": 200,
   #  "max_time" : 1,
    "max_early_stop": 100
}

## experiment for "max_fe"
# 10 -> 101 (epoch(1)* pop(50) + pop(50) + 1 = 101  # 101보다 작게 fe를 설정하면 가장 적게 돌아가도 101번이므로 항상 101번이됨
# 50 -> 101 (epoch(1)* pop(50) + pop(50) + 1 = 101
# 110-> 151 (epoch(2)* pop(50) + pop(50) + 1 = 151 # 예상 (실제로도 그럼)
# 152-> 201 (epoch(3)* pop(50) + pop(50) + 1 = 201 # 예상 (실제로도 그럼)
# 201-> 251 (epoch(3)* pop(50) + pop(50) + 1 = 201 # 예상 (하지만, 실제로는 251이됨)
# 200-> 201 (epoch(3)* pop(50) + pop(50) + 1 = 201 # 예상 (실제로도 201임)

## experiment for "max_time" (epoch=1000, pop_size=50, pc=0.85, pm=0.1) => 사용하지 않는게 좋을듯함.
# 설정 없이 수행 시간: 50051회 수행, 14.567774초
# 10초 설정 => 101회만 수행, 0.018001초 ==> ?? 10초만 실행하다가 멈춰야 하는데, 훨씬 적게 수행함
# 100초 설정 => 101회만 수행, 0.019006초 ==> ?? 50051회 모두다 실행되어야 할텐데, 훨씬 적게 수행됨
# 10000초 설정 => 101회만 수행, 0.019006초 ==> ?? 50051회 모두다 실행되어야 할텐데, 훨씬 적게 수행됨
# 10.5초 설정 => 101회만 수행, 0.018001초 ==> 혹시 flat? -> 아님!
# 1초 설정 => 101회 실행, ==> 반응이 없음

## experiment for "max_early_stop" (epoch=1000, pop_size=50, pc=0.85, pm=0.1) => 이것은 MAX로 할때 해볼만할듯함.
# max number of epoch로 K epoch이후에 더이상 fitness 값이 증가하지 않으면 바로 stop
# 30 => #2801 수행하다가 멈춤, fitness value = 6278.875213583084, 30 epoch라면 -> 30x50+50+1 => 1551 이후니까, 이후에 그정도까지 수행후 멈춰짐
# 50 => #7051 수행하다가 멈춤, fitness value = 4831.217145293109, 50 epoch라면 -> 50x50+50+1 => 2551 이후니까, 이후에 그정도까지 수행후 멈춰짐
# 100=> #12101 수행하다가 멈춤, fitness value = 3650.840828586948, 100 epoch라면 -> 100x50+50+1 => 5051 이후니까, 이후에 그정도까지 수행후 멈춰짐

# Use all available stopping conditions together
# term_dict = {
#    "max_epoch": 1100,
#    "max_fe": 80000,
#    "max_time": 10.5,
#    "max_early_stop": 500
# }

problem_dict = {
    "obj_func": objective_func,
    "bounds": FloatVar(lb=[-100, ] * 30, ub=[100, ] * 30,),
    "minmax": "min",
    "log_to"   : "file",
    "log_file" : "result.log",  # Default value = "mealpy.log"
}

# optimizer = GA.BaseGA(epoch=100, pop_size=50, pc=0.85, pm=0.1)
# optimizer.solve(problem_dict)


sw = StopWatch()
sw.start()
# base
# optimizer = GA.BaseGA(epoch=100, pop_size=50, pc=0.85, pm=0.1)
# optimizer.solve(problem_dict, termination=term_dict)


# optimizer = ABC.OriginalABC(epoch = 1000, pop_size = 50, n_limits = 50)
optimizer = GA.BaseGA(epoch=1000, pop_size=50, pc=0.85, pm=0.1)  ## ABC보다 좋은 성능을 보임
optimizer.solve(problem_dict, termination=term_dict)
# optimizer.solve(problem_dict)
print(f"Stopwatch: Computing GA =>  {sw.stop()}")


# optimizer = SMA.OriginalSMA(epoch=100, pop_size=50, pr=0.03)
# optimizer.solve(problem_dict)

# optimizer = SMA.OriginalSMA(epoch=100, pop_size=50, pr=0.03)
# optimizer.solve(problem_dict, termination=term_dict)

print(optimizer.g_best.solution)
print(optimizer.g_best.target.fitness)

