
import unittest
from multiprocessing import Pool, Process, Pipe, Lock, Value, Array, Manager
import os
import time
import multiprocessing as mp

def f(x):
    return x*x

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def f2(name):
    info('################ function f2')
    print('hello', name)

def foo(q):
    # print(f'foo:{q.get()}')
    q.put('hello')

def f3(conn):
    conn.send([42, None, 'hello'])
    conn.close()

def f4(l, i):
    l.acquire()
    try:
        print('hello world', i)
    finally:
        l.release()

def f5(n, a):
    n.value = 3.1415927
    for i in range(len(a)):
        a[i] = -a[i]

def f6(d, l):
    d[1] = '1'
    d['2'] = 2
    d[0.25] = None
    l.reverse()


def fx1(x, dic):
    info('################### fx1')
    print(f'[IN FUCTION] fx1:{x}')
    sum = 0
    for i in range(x):
        sum = sum + i * i
        time.sleep(0.01)

    dic['fx1'] = sum
    return x*x

def fx2(x, dic):
    info('################### fx2')
    print(f'[IN FUCTION] fx2:{x}')
    sum = 0
    for i in range(x):
        sum = sum + i * i * i
        time.sleep(0.01)
    dic['fx2'] = sum
    return x*x

def fx3(x, dic):
    info('################### fx3')
    print(f'[IN FUCTION] fx3:{x}')
    sum = 0
    for i in range(x):
        sum = sum + i * i * i * i
        time.sleep(0.01)

    dic['fx3'] = sum
    return x*x

''''
https://docs.python.org/ko/3/library/multiprocessing.html
'''
class MyTestCase(unittest.TestCase):

    def test_singleprocessing(self):
        start = time.time()

        result_dic = {}
        fx1(1001, result_dic)
        fx2(1002, result_dic)
        fx3(1003, result_dic)

        print(result_dic)
        end = time.time()
        elapsed_time = end - start
        print(f'Elapsed Time: {elapsed_time}')


    def test_singleprocessing2(self):
        def count(name):
            for i in range(1, 50000001):
                s = f'{name}: {i}'

        start = time.time()
        num_list = ['p1', 'p2', 'p3', 'p4']
        for num in num_list:
            count(num)
        end = time.time()
        elapsed_time = end - start
        print(f'Elapsed Time: {elapsed_time}')

    def test_multiprocessing_00(self):
        def count(name):
            for i in range(1, 50000001):
                s = f'{name}: {i}'

        start = time.time()
        num_list = ['p1', 'p2', 'p3', 'p4']

        pool = mp.Pool(processes=2)
        pool.map(count, num_list)
        pool.close()
        pool.join()
        end = time.time()
        elapsed_time = end - start
        print(f'Elapsed Time: {elapsed_time}')


    def test_multiprocessing_0(self):
        start = time.time()
        mp.set_start_method('spawn')
        info('MAIN')
        lock = Lock()
        procs = []
        with Manager() as manager:
            result_dic = manager.dict()
            for num in [1001, 1002, 1003, 1004]:
                if num % 3 == 0:
                    # p = Process(target=fx1, args=(lock, num))
                    p = Process(target=fx1, args=(1001, result_dic))
                    p.start()
                    procs.append(p)
                elif num % 3 == 1:
                    # p = Process(target=fx2, args=(lock, num))
                    p = Process(target=fx2, args=(1002, result_dic))
                    p.start()
                    procs.append(p)
                elif num % 3 == 2:
                    # p = Process(target=fx3, args=(lock, num))
                    p = Process(target=fx3, args=(1003, result_dic))
                    p.start()
                    procs.append(p)

            for p in procs:
                p.join()

            print(result_dic)

        end = time.time()
        elapsed_time = end - start
        print(f'Elapsed Time: {elapsed_time}')


    @unittest.skip("Tested")
    def test_multiprocessing_1(self):
        with Pool(5) as p:
            print(p.map(f, [1, 2, 3]))


    @unittest.skip("Tested")
    def test_multiprocessing_2(self):
        info('main line')
        p = Process(target=f2, args=('bob',))
        p.start()
        p.join()

    @unittest.skip("Tested")
    def test_multiprocessing_sharing_input_data_btw_process(self):
        mp.set_start_method('spawn')
        q = mp.Queue()
        p = mp.Process(target=foo, args=(q,))
        p.start()
        print(f'result: {q.get()}')
        p.join()
        print('done')

    @unittest.skip("Tested")
    def test_multiprocessing_sharing_input_data_btw_process2(self):
        parent_conn, child_conn = Pipe()
        p = Process(target=f3, args=(child_conn,))
        p.start()
        print(parent_conn.recv())  # prints "[42, None, 'hello']"
        p.join()

    @unittest.skip("Tested")
    def test_multiprocessing_sync(self):
        lock = Lock()
        for num in range(10):
            Process(target=f4, args=(lock, num)).start()

    @unittest.skip("Tested")
    def test_multiprocessing_shared_memory(self):
        num = Value('d', 0.0)
        arr = Array('i', range(10))

        p = Process(target=f5, args=(num, arr))
        p.start()
        p.join()

        print(num.value)
        print(arr[:])

    @unittest.skip("Tested")
    def test_multiprocessing_shared_memory2(self):
        '''
        list, dict, Namespace, Lock, RLock, Semaphore, BoundedSemaphore, Condition, Event, Barrier, Queue, Value
        :return:
        '''
        with Manager() as manager:
            d = manager.dict()
            l = manager.list(range(10))

            p = Process(target=f6, args=(d, l))
            p.start()
            p.join()

            print(d)
            print(l)


def count(name):
    for i in range(1, 50000001):
        s = f'{name}: {i}'

if __name__ == '__main__':
    unittest.main()
