import argparse
import sys
import unittest

from bt4.Constants import ExType, QUOTE_MODE
from bt3_config.quote_conf import QUOTE_PARAMS
from bt4.utils.bt4_cli_args import get_argument, get_eqd_argument

import bt4.GlobalProperties as global_prop

class MyTestCase(unittest.TestCase) :

    def test_exec_bt_with_arguments(self) :
        sys.argv = ['BullTraderMain', 'bt', '-tid', '209', '-enable_bulk', 'true',
                    '-redis', '127.0.0.22:6379',
                    '-postgre', '192.168.1.21:5432', '-postgre_db', 'bt4_test']
        print(sys.argv)
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

    def test_argument_bt1(self) :
        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

        sys.argv = ['BullTraderMain', 'bt', '-tid', '123', '-enable_bulk', 'false',
                    '-redis', '123.123.123.123:4444','-postgre', '111.111.11.11:1234','-postgre_db', 'bt5_test']
        arg_map = get_argument()
        print(arg_map)

        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

    def test_argument_bt2(self) :
        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

        sys.argv = ['BullTraderMain', 'bt', '-tid', '123',
                    '-redis', '123.123.123.123:4444','-postgre', '111.111.11.11:1234','-postgre_db', 'bt4_test']
        arg_map = get_argument()
        print(arg_map)

        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

    def test_argument_bt3(self) :
        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

        sys.argv = ['BullTraderMain', 'bt', '-tid', '123',
                    '-postgre', '111.111.11.11:1234','-postgre_db', 'bt4_test']
        arg_map = get_argument()
        print(arg_map)

        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

    def test_argument_bt4(self) :
        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

        sys.argv = ['BullTraderMain', 'bt', '-tid', '123',
                    '-postgre_db', 'bt4_test']
        arg_map = get_argument()
        print(arg_map)

        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

    def test_argument_ft1(self) :
        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

        sys.argv = ['BullTraderMain', 'ft', '-tid', '123', '-account', 'abcde',
                    '-redis', '123.123.123.123:4444','-postgre', '111.111.11.11:1234','-postgre_db', 'bt5_test']
        arg_map = get_argument()
        print(arg_map)

        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

    def test_argument_ft2(self) :
        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

        # sys.argv = ['BullTraderMain', 'ft', '-tid', '123', '-account', 'stkim']
        sys.argv = ['BullTraderMain', 'ft', '-h']
        arg_map = get_argument()
        print(arg_map)

        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

    def test_argument_eqd1(self) :
        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

        # sys.argv = ['BullTraderMain', 'ft', '-tid', '123', '-account', 'stkim']
        sys.argv = ['ExchangeQuoteDispatcherMain', '-quote_mode', 'redis_kafka',
                    '-redis', "localhost:2222",
                    "-kafka", "123.12.2.1:3333"]
        arg_map = get_eqd_argument()
        print(arg_map)

        print(f"{global_prop.redis_svr=}")
        print(f"{global_prop.postgre_sql_svr=}")
        print(f"{global_prop.postgre_sql_db=}")
        print(f"{global_prop.enable_bulk=}")
        print(f"{global_prop.REDIS_HOST=}")
        print(f"{global_prop.REDIS_PORT=}")
        print(f"{global_prop.DATABASE_URI=}")
        print(f"{global_prop.DATABASE_PORT=}")

if __name__ == '__main__' :
    unittest.main()
