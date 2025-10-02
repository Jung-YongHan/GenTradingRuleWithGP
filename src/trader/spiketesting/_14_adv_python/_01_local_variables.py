import copy
import unittest


class MyTestCase(unittest.TestCase) :
    def test_something(self) :
        a = "a"
        b = "b"

        cloned_locals = copy.copy(locals())
        for loc in cloned_locals:
            print(f"{loc} - {cloned_locals[loc]}")


if __name__ == '__main__' :
    unittest.main()
