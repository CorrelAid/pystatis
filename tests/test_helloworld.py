from pystatis import logincheck, whoami
from tests.test_http_helper import _generic_request_status


def test_whoami(mocker):
    mocker.patch(
        "pystatis.helloworld.load_config",
        return_value={
            "GENESIS API": {
                "base_url": "mocked_url",
                "username": "JaneDoe",
                "password": "password",
            }
        },
    )

    mocker.patch(
        "pystatis.helloworld.requests.get",
        return_value=_generic_request_status(),
    )

    response = whoami()

    assert response == str(_generic_request_status().text)


def test_logincheck(mocker):
    mocker.patch(
        "pystatis.helloworld.load_config",
        return_value={
            "GENESIS API": {
                "base_url": "mocked_url",
                "username": "JaneDoe",
                "password": "password",
            }
        },
    )
    mocker.patch(
        "pystatis.helloworld.requests.get",
        return_value=_generic_request_status(),
    )

    response = logincheck()

    assert response == str(_generic_request_status().text)
