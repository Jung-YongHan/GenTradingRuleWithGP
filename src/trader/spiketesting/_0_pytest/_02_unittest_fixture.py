import unittest

import pytest
from parameterized import parameterized

want_to_execute = 1

class MyTestCase(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def prepare_fixture(self, calculator):
        self.calculator = calculator

    @unittest.skipIf(want_to_execute != 1, "")
    def test_add(self):
        assert self.calculator.add(1, 2) == 3
        assert self.calculator.add(2, 2) == 4

    @unittest.skipIf(want_to_execute != 2, "")
    def test_subtract(self):
        assert self.calculator.subtract(5, 1) == 4
        assert self.calculator.subtract(3, 2) == 1

    @unittest.skipIf(want_to_execute != 3, "")
    def test_multiply(self):
        assert self.calculator.multiply(2, 2) == 4
        assert self.calculator.multiply(5, 6) == 30

    @unittest.skipIf(want_to_execute != 4, "")
    def test_divide(self):
        assert self.calculator.divide(8, 2) == 4
        assert self.calculator.divide(9, 3) == 3

    @unittest.skipIf(want_to_execute != 5, "")
    @parameterized.expand([
        ["One", "Two"],
        ["Three", "Four"],
        ["Five", "Six"],
    ])
    def test_parameterized(self, arg1, arg2):
        print(arg1, arg2)

if __name__ == '__main__':
    unittest.main()
