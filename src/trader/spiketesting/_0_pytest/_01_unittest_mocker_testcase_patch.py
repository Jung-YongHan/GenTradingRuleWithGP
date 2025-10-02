### Source : https://www.daleseo.com/python-unittest-mock-patch/

import unittest
from unittest.mock import patch

##########################################################
## Target Code #1
from spiketesting._0_pytest.file import ProductionClass


def hello():
    return "Hello!"

##########################################################
## Target Code #2
import requests
def get_user(id):
    response = requests.get(f"https://jsonplaceholder.typicode.com/users/{id}")
    if response.status_code != 200:
        raise Exception("Failed to get a user.")
    return response.json()

def create_user(user):
    response = requests.post(f"https://jsonplaceholder.typicode.com/users", data=user)
    if response.status_code != 201:
        raise Exception("Failed to create a user.")
    return response.json()

control_test_case_exec = False

class MyTestCase(unittest.TestCase):

    ## Test code for the target code #1
    @unittest.skipIf(control_test_case_exec == True, 'This is controlled test case!')
    @patch("spiketesting._0_pytest._01_unittest_mocker_testcase_patch.hello", return_value="Mock!!")
    def test_hello(self, mock_hello):
        self.assertEqual(hello(), "Mock!!")
        self.assertIs(hello, mock_hello)
        mock_hello.assert_called_once_with()

    @unittest.skipIf(control_test_case_exec == True, 'This is controlled test case!')
    @patch("requests.get")
    def test_get_user(self, mock_get):
        response = mock_get.return_value
        response.status_code = 200
        response.json.return_value = {
            "name": "Test User",
            "email": "user@test.com",
        }

        ## fetched method
        user = get_user(1)

        self.assertEqual(user["name"], "Test User")
        self.assertEqual(user["email"], "user@test.com")
        mock_get.assert_called_once_with("https://jsonplaceholder.typicode.com/users/1")

    @unittest.skipIf(control_test_case_exec == True, 'This is controlled test case!')
    @patch("requests.post")
    def test_create_user(self, mock_post):
        response = mock_post.return_value
        response.status_code = 201
        response.json.return_value = {"id": 99}

        user = create_user(
            {"name": "Test User", "email": "user@test.com",}
        )

        self.assertEqual(user["id"], 99)
        mock_post.assert_called_once_with(
            "https://jsonplaceholder.typicode.com/users",
            data={"name": "Test User", "email": "user@test.com",},
        )

    @unittest.skipIf(control_test_case_exec == True, 'This is controlled test case!')
    def test_patch_object(self):
        with patch.object(ProductionClass, 'test_method', return_value=None) as mock_method:
            thing = ProductionClass()
            print(thing.test_method(1, 2, 3))

        print(mock_method.assert_called_once_with(1, 2, 3))

    @unittest.skipIf(control_test_case_exec == True, 'This is controlled test case!')
    def test_patch_dict(self):
        foo = {'key': 'value'}
        print(f'{foo=}')
        original = foo.copy()
        with patch.dict(foo, {'newkey': 'newvalue'}, clear=True):
            print(f'{foo=}')
            assert foo == {'newkey': 'newvalue'}

        assert foo == original

if __name__ == '__main__':
    unittest.main()
