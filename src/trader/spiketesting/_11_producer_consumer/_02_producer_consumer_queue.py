
import logging
import random
import threading
import time
import unittest

from tornado import concurrent




class MyTestCase(unittest.TestCase) :

    def test_producer_consumer_buffer(self) :
        from spiketesting._11_producer_consumer._01_producer_consumer_support import Pipeline, producer, consumer
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format = format, level = logging.INFO,
                            datefmt = "%H:%M:%S")
        # logging.getLogger().setLevel(logging.DEBUG)

        pipeline = Pipeline()
        with concurrent.futures.ThreadPoolExecutor(max_workers = 2) as executor :
            executor.submit(producer, pipeline)
            executor.submit(consumer, pipeline)


    def test_producer_consumer_quqeue(self) :
        from spiketesting._11_producer_consumer._02_producer_consumer_support import Pipeline, producer, consumer
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format = format, level = logging.INFO,
                            datefmt = "%H:%M:%S")
        # logging.getLogger().setLevel(logging.DEBUG)

        pipeline = Pipeline()
        event = threading.Event()

        with concurrent.futures.ThreadPoolExecutor(max_workers = 2) as executor :
            # executor.submit(producer, pipeline, event)
            executor.submit(consumer, pipeline, event)

            while not event.is_set() :
                message = random.randint(1, 101)
                logging.info("Producer got message: %s", message)
                pipeline.set_message(message, "Producer")

            time.sleep(0.1)
            logging.info("Main: about to set event")
            event.set()

if __name__ == '__main__' :
    unittest.main()
