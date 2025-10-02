
import logging
import unittest

from tornado import concurrent

from spiketesting._11_producer_consumer._01_producer_consumer_support import Pipeline, producer, consumer


class MyTestCase(unittest.TestCase) :
    def test_producer_consumer(self) :
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format = format, level = logging.DEBUG,
                            datefmt = "%H:%M:%S")
        # logging.getLogger().setLevel(logging.DEBUG)

        pipeline = Pipeline()
        with concurrent.futures.ThreadPoolExecutor(max_workers = 2) as executor :
            executor.submit(producer, pipeline)
            executor.submit(consumer, pipeline)


if __name__ == '__main__' :
    unittest.main()
