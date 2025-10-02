
## 모든 테스트 코드에서는 해당 fixture들을 공유하여 사용할 수 있습니다.
## 알아서 pytest에서 공유해주는 마법!
import pytest

from spiketesting._0_pytest.calculator import Calculator

@pytest.fixture
def calculator():
    calculator = Calculator()
    return calculator
