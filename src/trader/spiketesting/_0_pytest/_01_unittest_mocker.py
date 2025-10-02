
from spiketesting._0_pytest import file


def test_mocker(mocker):
    mocker.patch("spiketesting._0_pytest.file.target_mock", return_value="mock 성공!")

    actual = file.target_mock()
    expected = "mock 성공!"
    assert actual == expected


