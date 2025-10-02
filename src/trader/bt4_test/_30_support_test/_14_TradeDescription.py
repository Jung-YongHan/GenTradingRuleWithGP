import os
import unittest
from os.path import dirname, join
import pandas as pd

class MyTestCase(unittest.TestCase) :
    def test_description(self) :
        root_dir = dirname(dirname(dirname(__file__)))
        csv_path = join(root_dir, f"log{os.sep}3404.csv")
        csv_df = pd.read_csv(csv_path, index_col = 0, parse_dates = True)

        print(csv_df.head())
        markets = ["KRW-BTC", "KRW-ETH", "KRW-XRP"]

        cols = csv_df.columns

        def __build_desc__(row, market, order):
            if order == "BUY":
                buy_system_key = f"{market}_buy_system"
                desc = ""
                for idx in range(1, 100) :
                    if f"{buy_system_key}{idx}" in row:
                        if row[f"{buy_system_key}{idx}"] == True:
                            desc = f"{desc} \n {buy_system_key}{idx}( {row[f'{buy_system_key}{idx}']} ) => {row[f'{buy_system_key}{idx}_desc']}"
                    else:
                        break
                return desc
            elif order == "SELL":
                sell_system_key = f"{market}_sell_system"
                desc = ""
                for idx in range(1, 100) :
                    if f"{sell_system_key}{idx}" in row :
                        if row[f"{sell_system_key}{idx}"] == True :
                            desc = f"{desc} \n {sell_system_key}{idx}( {row[f'{sell_system_key}{idx}']} ) => {row[f'{sell_system_key}{idx}_desc']}"
                    else :
                        break
                return desc
            else:
                print("It should never gonna happen!")
                return ""

        def collect_desc(row, markets):
            for market in markets:
                if row[f"{market}_order"] == "BUY":
                    desc = __build_desc__(row, market, "BUY")
                    print(f"BUY (True) ==> {desc}")

                if row[f"{market}_order"] == "SELL":
                    desc = __build_desc__(row, market, "SELL")
                    print(f"SELL (True) ==> {desc}")


        csv_df.apply(collect_desc, axis = 1, args=(markets,))




if __name__ == '__main__' :
    unittest.main()
