import unittest

import sys


class MyTestCase(unittest.TestCase):

    def test_eqd_exec(self) :

        # sys.argv = ["ExchangeQuoteDispatcher", "-quote_mode", "kafka",
        #             "-kafka", "123.12.2.1:3333"]
        sys.argv = ["ExchangeQuoteDispatcher", "-quote_mode", "redis_kafka"]
        import bt4.exec.ExchangeQuoteDispatcherMain as eqdm
        eqdm.main(sys.argv)


if __name__ == '__main__':
    unittest.main()
