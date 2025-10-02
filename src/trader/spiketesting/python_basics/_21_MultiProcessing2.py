
from multiprocessing import Pool, Process, Pipe, Lock, Value, Array, Manager
import os
import time
import multiprocessing as mp
from functools import partial

def count(name):
    for i in range(1, 50000001):
        s = f'{name}: {i}'

def foo(x,y,z):
    return x*y*z

def foo_multi_results(x,y,z):
    return x*y*z, (x+1)*(y+1)*(z+1), (x+2)*(y+2)*(z+2)


if __name__ == '__main__':

    ## Single Process
    # start = time.time()
    # num_list = ['p1', 'p2', 'p3', 'p4']
    # for num in num_list:
    #     count(num)
    # end = time.time()
    # elapsed_time = end - start
    # print(f'Elapsed Time: {elapsed_time}')

    ## Multi Process
    # start = time.time()
    # num_list = ['p1', 'p2', 'p3', 'p4']
    #
    # pool = mp.Pool(processes=8)
    # pool.map(count, num_list)
    # pool.close()
    # pool.join()
    # end = time.time()
    # elapsed_time = end - start
    # print(f'Elapsed Time: {elapsed_time}')

    ### Multiple Params
    # pool = mp.Pool(processes=4)
    # func = partial(foo, y=2, z=3)
    # result = pool.map(func, [1,2,4,5])
    # pool.close()
    # pool.join()
    # print(result)

    print(f'cpu: {mp.cpu_count()}')
    pool = mp.Pool(processes=mp.cpu_count() * 2)
    func = partial(foo_multi_results, y=2, z=3)
    result = pool.map(func, [1,2,4,5])
    pool.close()
    pool.join()
    print(result)

    result_1, result_2, result_3 = [], [], []
    for i in result:
        result_1.append(i[0])
        result_2.append(i[1])
        result_3.append(i[2])

    print(result_1)
    print(result_2)
    print(result_3)