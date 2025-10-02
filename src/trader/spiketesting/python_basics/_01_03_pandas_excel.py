import unittest
import pandas as pd
from os.path import dirname, join
import re

def _excel_sheet_name_for_market(source):
    pattern_text = '[A-Z]+[A-Z]+[A-Z]+-[A-Z]*'
    pattern = re.compile(pattern_text)
    m = pattern.match(source)
    return bool(m)

class MyTestCase(unittest.TestCase):

    # @unittest.skip("Tested")
    def test_dataframe_excel(self):
        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data_validation\\validation_data_v1.xlsx')

        data = {}
        with pd.ExcelFile(file_name) as xlsx:
            for sheet_name in xlsx.sheet_names:
                print(sheet_name)
                if _excel_sheet_name_for_market(sheet_name):
                    data[sheet_name] = xlsx.parse(sheet_name)
                    print(type(data[sheet_name]))
                    print(data[sheet_name])

if __name__ == '__main__':
    unittest.main()
