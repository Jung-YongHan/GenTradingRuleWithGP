import asyncio
import random
import time
import unittest

from bt4.utils.python_utils import start_timing, end_n_elapsed_time


class MyTestCase(unittest.TestCase) :

    async def do_my_job(self, param):
        sleep_time = random.randint(1,3)
        print(f'do my job! : {param} for {sleep_time} sec')
        await asyncio.sleep(sleep_time)
        return param, sleep_time

    async def main_job(self):
        results = await asyncio.wait([
            asyncio.create_task(self.do_my_job(1)),
            asyncio.create_task(self.do_my_job(2)),
            asyncio.create_task(self.do_my_job(3))])

        for result in results[0]:
            print(result.result())

    def test_something(self) :
        start = start_timing()
        asyncio.run(self.main_job())
        print('done!')
        print(end_n_elapsed_time(start, 'async jobs'))



if __name__ == '__main__' :
    unittest.main()
