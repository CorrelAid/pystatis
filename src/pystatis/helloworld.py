"""Module provides wrapper for HelloWorld GENESIS REST-API functions."""

import requests

from pystatis.config import load_config
from pystatis.http_helper import _check_invalid_status_code


def whoami() -> str:
    """
    Wrapper method which constructs an URL for testing the Destatis API
    whoami method, which returns host name and IP address.

    Returns:
        str: text test response from Destatis
    """
    config = load_config()
    url = f"{config['GENESIS API']['base_url']}" + "helloworld/whoami"

    response = requests.get(url, timeout=(1, 15))

    _check_invalid_status_code(response)

    return str(response.text)


def logincheck() -> str:
    """
    Wrapper method which constructs an URL for testing the Destatis API
    logincheck method, which tests the login credentials (from the config.ini).

    Returns:
        str: text logincheck response from Destatis
    """
    config = load_config()
    url = f"{config['GENESIS API']['base_url']}" + "helloworld/logincheck"

    params = {
        "username": config["GENESIS API"]["username"],
        "password": config["GENESIS API"]["password"],
    }

    response = requests.get(url, params=params, timeout=(1, 15))

    # NOTE: Cannot use get_data_from_endpoint due to colliding
    # and misleading usage of "Status" key in API response
    _check_invalid_status_code(response)

    return str(response.text)
