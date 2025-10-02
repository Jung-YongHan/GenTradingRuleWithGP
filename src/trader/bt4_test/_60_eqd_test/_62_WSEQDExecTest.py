import unittest

import sys


class MyTestCase(unittest.TestCase):

    def test_ws_eqd_exec_binance(self) :
        sys.argv = ["WS_Dispatcher", "-ex_type", "binance"]
        import bt4.exec.WebsocketExQuoteDispatcherMain as ws_eqdm
        ws_eqdm.ws_main(sys.argv)

    def test_ws_eqd_exec_upbit(self) :
        sys.argv = ["WS_Dispatcher", "-ex_type", "upbit"]
        import bt4.exec.WebsocketExQuoteDispatcherMain as ws_eqdm
        ws_eqdm.ws_main(sys.argv)

    def test_ws_eqd_exec_bithumb(self) :
        sys.argv = ["WS_Dispatcher", "-ex_type", "bithumb"]
        import bt4.exec.WebsocketExQuoteDispatcherMain as ws_eqdm
        ws_eqdm.ws_main(sys.argv)

if __name__ == '__main__':
    unittest.main()
