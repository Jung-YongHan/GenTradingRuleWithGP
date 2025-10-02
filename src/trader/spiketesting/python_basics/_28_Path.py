import os
import unittest
from os.path import dirname, join
import pickle

class MyTestCase(unittest.TestCase) :
    def test_something(self) :

        my_dict = {'abc': 'def', 'daf':'asdf'}
        root = dirname(__file__)
        file_path = join(root, 'ccccccccccccccccccccccccc.txt')
        if os.path.exists(file_path):

            f = open(file_path, mode = 'rb')
            my_loaded_dict = pickle.load(f)
            f.close()
            print(f'loaded dict = {my_loaded_dict}')

            f = open(file_path, mode = 'wb')
            my_loaded_dict['abc'] =  my_loaded_dict['abc'] + 'axxx'
            pickle.dump(my_loaded_dict, f)
            f.close()
        else:
            f = open(file_path, mode = 'wb')
            pickle.dump(my_dict, f)
            f.close()

        print()


if __name__ == '__main__' :
    unittest.main()
