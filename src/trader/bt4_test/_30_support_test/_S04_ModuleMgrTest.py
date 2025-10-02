import os
import unittest
from os.path import dirname, join

from bt4.utils.module_support import ModuleManager


class MyTestCase(unittest.TestCase) :
    def test_accessing_module(self) :
        module_name =  "bt4.GlobalProperties"
        mm = ModuleManager(module_name)
        print(mm.get_variable("kafka_bootstrap_svr"))
        print(mm.set_variable("kafka_bootstrap_svr", "123.123.123.123:1111"))
        print(mm.get_variable("kafka_bootstrap_svr"))






if __name__ == '__main__' :
    unittest.main()
