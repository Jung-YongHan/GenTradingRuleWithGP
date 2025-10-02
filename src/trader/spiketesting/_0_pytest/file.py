#####################
def target_mock():
    return "mock 실패!"

class ProductionClass:
    def __init__(self):
        pass

    def test_method(self, a, b, c, key):
        print(f'{a=},{b=},{c=},{key=}')