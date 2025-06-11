"""Module provides wrapper for HelloWorld GENESIS REST-API functions."""

import requests

from pystatis import db
from pystatis.http_helper import _check_invalid_status_code


def whoami(db_name: str) -> str:
    """
    Wrapper method which constructs a URL for testing the Destatis API
    whoami method, which returns host name and IP address.

    Args:
        db_name (str): Name of the database to test

    Returns:
        str: text test response from Destatis
    """
    url = f"{db.get_host(db_name)}" + "helloworld/whoami"

    try:
        response = requests.get(url, timeout=(30, 15))
    except requests.exceptions.Timeout:
        raise TimeoutError("Login request timed out after 15 minutes")

    _check_invalid_status_code(response)

    return str(response.text)


def logincheck(db_name: str) -> str:
    """
    Wrapper method which constructs a URL for testing the Destatis API
    logincheck method, which tests the login credentials (from the config.ini).

    In addition, this method automatically terminates requests
    that have been running for longer than 15 minutes if too many requests are running in parallel.
    This method restores the ability to work by cleaning up if the limit has been exceeded.

    Args:
        db_name (str): Name of the database to login to

    Returns:
        str: text logincheck response from Destatis
    """
    db_host, db_user, db_pw = db.get_settings(db_name)
    url = f"{db_host}helloworld/logincheck"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "username": db_user,
        "password": db_pw,
    }
    params = {
        "language": "de",
    }

    response = requests.post(url, headers=headers, data=params, timeout=(30, 15))

    # NOTE: Cannot use get_data_from_endpoint due to colliding
    # and misleading usage of "Status" key in API response
    _check_invalid_status_code(response)

    return str(response.text)
