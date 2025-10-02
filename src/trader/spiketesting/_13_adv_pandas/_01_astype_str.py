import unittest
import pandas as pd

class MyTestCase(unittest.TestCase) :
    def test_something(self) :
        raw_data = {'col0' : [1, 2, 3, 4],
                    'col1' : [10, 20, 30, 40],
                    'col2' : [100, 200, 300, 400]}
        df = pd.DataFrame(raw_data)

        value = "-50"
        print(len(value))

        print(df["col0"].astype(str))
        print( pd.Series(df["col0"]).astype(str))

        value = -50
        print( pd.Series(value).astype(str))


if __name__ == '__main__' :
    unittest.main()
