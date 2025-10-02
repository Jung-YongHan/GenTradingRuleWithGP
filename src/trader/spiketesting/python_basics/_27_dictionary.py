import unittest

from bt4.utils.python_utils import convert_list_to_tuple_of_dict, dict_to_key


class MyTestCase(unittest.TestCase) :
    def test_something(self) :
        key_dict = {}
        key_dict['abc'] = [123, 456]
        key_dict['def'] = 'abd'
        key_dict['ghi'] = 213
        key_dict['jkl'] = 125

        key_dict = convert_list_to_tuple_of_dict(key_dict)
        key = dict_to_key(key_dict)
        result_cache = {}

        value = 'xxxx'
        result_cache[key] = value
        print(result_cache[key])

        key_dict2 = {}
        key_dict2['abc'] = [123, 456]
        key_dict2['def'] = 'abd'
        key_dict2['ghi'] = 213
        key_dict2['jkl'] = 125

        key_dict2 = convert_list_to_tuple_of_dict(key_dict2)
        key2 = dict_to_key(key_dict2)

        if key2 in result_cache:
            result = result_cache[key2]
            print(result)
            self.assertEqual(value, result)




if __name__ == '__main__' :
    unittest.main()
