import unittest
from unittest.mock import MagicMock, Mock

from spiketesting._0_pytest.file import ProductionClass


class MyTestCase(unittest.TestCase):

    # @unittest.skip
    def test_mock_method(self):
        """
        Mocking test_method of ProductionClass
        :return:
        """
        thing = ProductionClass()
        thing.test_method = MagicMock(return_value = 5)
        ret = thing.test_method(3,4,5, key='value')
        print(f'\nXXXXXXXXX{ret=}')
        thing.test_method.assert_called_with(3, 4, 5, key='value')

    @unittest.skip
    def test_side_effect(self):
        mock = Mock(side_effect=KeyError('foo'))
        # mock()
        values = {'a': 1, 'b': 2, 'c': 3}

        def side_effect(arg):
            return values[arg]

        mock.side_effect = side_effect
        print(mock('a'), mock('b'), mock('c'))

        # mock.side_effect = [5, 4, 3, 2, 1]      ## 호출할때 해당 순서로 결과값을 리턴해줌!!
        mock.side_effect = ['a', 'b', 'c', 'd', 'e']  ## 호출할때 해당 순서로 결과값을 리턴해줌!!
        print(mock(), mock(), mock(), mock(), mock())

if __name__ == '__main__':
    unittest.main()
