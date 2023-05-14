import json
import logging
from pathlib import Path

import pytest
import requests

from pystatis.config import load_config
from pystatis.custom_exceptions import DestatisStatusError
from pystatis.http_helper import (
    _check_invalid_destatis_status_code,
    _check_invalid_status_code,
    get_data_from_endpoint,
    get_data_from_resultfile,
    get_job_id_from_response,
    load_data,
    start_job,
)


def _generic_request_status(
    status_response: bool = True,
    status_code: int = 200,
    code: int = 0,
    status_type: str = "Information",
    status_content: str = "Erfolg/ Success/ Some Issue",
) -> requests.Response:
    """
    Helper method which allows to create a generic request.Response that covers all Destatis answers

    Returns:
        requests.Response: the response from Destatis
    """
    # define possible status dict and texts
    status_dict = {
        "Ident": {
            "Service": "A DESTATIS service",
            "Method": "A DESTATIS method",
        },
        "Status": {
            "Code": code,
            "Content": status_content,
            "Type": status_type,
        },
    }

    response_text = "Some text for a successful response without status..."

    # set up generic requests.Response
    request_status = requests.Response()
    request_status.status_code = status_code  # success

    # Define UTF-8 encoding as requests guesses otherwise
    if status_response:
        request_status._content = json.dumps(status_dict).encode("UTF-8")
    else:
        request_status._content = response_text.encode("UTF-8")

    return request_status


def test_get_response_from_endpoint(mocker):
    """
    Test once with generic API response, more detailed tests
    of subfunctions and specific cases below.
    """
    mocker.patch(
        "pystatis.http_helper.requests", return_value=_generic_request_status()
    )
    mocker.patch(
        "pystatis.http_helper.load_config",
        return_value={
            "GENESIS API": {
                "base_url": "mocked_url",
                "username": "JaneDoe",
                "password": "password",
            }
        },
    )

    get_data_from_endpoint(endpoint="endpoint", method="method", params={})


def test_check_invalid_status_code_with_error():
    """
    Basic tests to check an error status code (4xx, 5xx)
    for _handle_status_code method.
    """
    for status_code in [400, 500]:
        with pytest.raises(requests.exceptions.HTTPError) as e:
            _check_invalid_status_code(
                _generic_request_status(status_code=status_code)
            )
        assert (
            str(e.value) == f"The server returned a {status_code} status code."
        )


def test_check_invalid_status_code_without_error():
    """
    Basic test to check a valid status code (2xx)
    for the _handle_status_code method.
    """
    try:
        _check_invalid_status_code(_generic_request_status())
    except Exception:
        assert False


def test_check_invalid_destatis_status_code_with_error():
    """
    Basic tests to check an error status code as defined in the
    documentation via code (e.g. -1, 104) or type ('Error', 'Fehler').
    """
    for status in [
        _generic_request_status(code=104),
        _generic_request_status(status_type="Error"),
        _generic_request_status(status_type="Fehler"),
    ]:
        # extract status content which is raised
        status_content = status.json().get("Status").get("Content")

        with pytest.raises(DestatisStatusError) as e:
            _check_invalid_destatis_status_code(status)
        assert str(e.value) == status_content

    # also test generic -1 error code
    generic_error_status = _generic_request_status(
        code=-1,
        status_content="Error: There is a system error. Please check your query parameters.",
    )

    with pytest.raises(DestatisStatusError) as e:
        _check_invalid_destatis_status_code(generic_error_status)
    assert (
        str(e.value)
        == "Error: There is a system error. Please check your query parameters."
    )


def test_check_invalid_destatis_status_code_with_warning(caplog):
    """
    Basic tests to check a warning status code as defined in the
    documentation via code (e.g. 22) or type ('Warning', 'Warnung').
    """
    caplog.set_level(logging.WARNING)

    for status in [
        _generic_request_status(code=22),
        _generic_request_status(status_type="Warnung"),
        _generic_request_status(status_type="Warning"),
    ]:
        # extract status content which is contained in warning
        status_content = status.json().get("Status").get("Content")

        _check_invalid_destatis_status_code(status)

        assert status_content in caplog.text


def test_check_invalid_destatis_status_code_without_error(caplog):
    """
    Basic tests to check the successful status code 0 or only text response as defined in the documentation.
    """
    # JSON response with status code
    caplog.set_level(logging.INFO)
    status = _generic_request_status()
    status_content = status.json().get("Status").get("Content")
    _check_invalid_destatis_status_code(status)

    assert status_content in caplog.text

    # text only response
    status_text = _generic_request_status(status_response=False)
    try:
        _check_invalid_destatis_status_code(status_text)
    except Exception:
        assert False


def test_get_job_id_from_response():
    response = requests.Response()
    response._content = """{"Status": {"Content": "Der Bearbeitungsauftrag wurde erstellt. Die Tabelle kann in Kürze als Ergebnis mit folgendem Namen abgerufen werden: 42153-0001_001597503 (Mindestens ein Parameter enthält ungültige Werte. Er wurde angepasst, um den Service starten zu können.: stand"}}""".encode()
    job_id = get_job_id_from_response(response)
    assert job_id == "42153-0001_001597503"


def test_get_job_id_from_response_with_no_id():
    response = requests.Response()
    response._content = """{"Status": {"Content": "Der Bearbeitungsauftrag wurde erstellt."}}""".encode()
    job_id = get_job_id_from_response(response)
    assert job_id == ""


def test_get_job_id_from_response_with_no_json():
    response = requests.Response()
    response._content = "Der Bearbeitungsauftrag wurde erstellt. Die Tabelle kann in Kürze als Ergebnis mit folgendem Namen abgerufen werden: 42153-0001_001597503 (Mindestens ein Parameter enthält ungültige Werte. Er wurde angepasst, um den Service starten zu können.: stand".encode()
    job_id = get_job_id_from_response(response)
    assert job_id == ""


def test_load_data_from_cache(mocker):
    # Setup
    config = load_config()
    cache_dir = Path(config["DATA"]["cache_dir"])
    name = "dummy_name"
    params = {"name": name}
    data = "test data"
    _hit_in_cash = mocker.patch(
        "pystatis.http_helper.hit_in_cash", return_value=True
    )
    _read_from_cache = mocker.patch(
        "pystatis.http_helper.read_from_cache", return_value=data
    )

    # Execution
    result = load_data("data", "", params)

    # Assertion
    assert result == data
    _hit_in_cash.assert_called_once_with(cache_dir, name, params)
    _read_from_cache.assert_called_once_with(cache_dir, name, params)


def test_start_job(mocker, caplog):
    caplog.set_level(logging.WARNING)

    mocker.patch(
        "pystatis.http_helper.get_data_from_endpoint",
        return_value=_generic_request_status(),
    )

    response = start_job(endpoint="dummy", method="dummy", params={})

    assert (
        "Die Tabelle ist zu groß, um direkt abgerufen zu werden. Es wird eine Verarbeitung im Hintergrund gestartet."
        in caplog.text
    )
    assert response._content == _generic_request_status()._content


def test_get_data_from_resultfile(mocker):
    response_job_in_progress = requests.Response()
    response_job_in_progress._content = (
        """{"List": [{"State": "Fertig"}]}""".encode()
    )
    response_finished_job = requests.Response()
    response_finished_job._content = """data_dummy""".encode()
    mocker.patch(
        "pystatis.http_helper.get_data_from_endpoint",
        side_effect=[response_job_in_progress, response_finished_job],
    )

    raw_data = get_data_from_resultfile("")

    assert raw_data == "data_dummy"


def test_load_data_data_endpoint(mocker):
    mocker.patch(
        "pystatis.http_helper.get_data_from_endpoint",
        return_value=_generic_request_status(),
    )
    # avoid caching
    mocker.patch("pystatis.http_helper.cache_data", return_value=None)

    data = load_data(endpoint="data", method="", params={})

    assert isinstance(data, str)
    assert data == _generic_request_status().text


def test_load_data_data_endpoint_data_no_status_code(mocker):
    response = requests.Response()
    response._content = """{"Status": {"Content": "Content"}}""".encode()
    mocker.patch(
        "pystatis.http_helper.get_data_from_endpoint", return_value=response
    )
    # avoid caching
    mocker.patch("pystatis.http_helper.cache_data", return_value=None)

    data = load_data(endpoint="data", method="", params={})

    assert isinstance(data, str)
    assert data == response.text


def test_load_data_data_endpoint_job(mocker):
    mocker.patch(
        "pystatis.http_helper.get_data_from_endpoint",
        return_value=_generic_request_status(code=98),
    )
    start_job_response = requests.Response()
    start_job_response._content = """{"Status": {"Content": "Der Bearbeitungsauftrag wurde erstellt."}}""".encode()
    mocker.patch(
        "pystatis.http_helper.start_job", return_value=start_job_response
    )
    mocker.patch(
        "pystatis.http_helper.get_data_from_resultfile",
        return_value="dummy_data",
    )
    # avoid caching
    mocker.patch("pystatis.http_helper.cache_data", return_value=None)

    data = load_data(endpoint="data", method="", params={"name": "11111-0001"})

    assert isinstance(data, str)
    assert data == "dummy_data"


def test_load_data_other_endpoints(mocker):
    mocker.patch(
        "pystatis.http_helper.get_data_from_endpoint",
        return_value=_generic_request_status(),
    )

    for as_json in [True, False]:
        data = load_data(endpoint="", method="", params={}, as_json=as_json)

        if as_json:
            assert isinstance(data, dict)
            assert data == _generic_request_status().json()
        else:
            assert isinstance(data, str)
            assert data == _generic_request_status().text
