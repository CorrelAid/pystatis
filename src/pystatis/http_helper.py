"""Wrapper module for the data endpoint."""
import json
import logging
import re
import time
from pathlib import Path
from typing import Union

import requests

from pystatis.cache import (
    cache_data,
    hit_in_cash,
    normalize_name,
    read_from_cache,
)
from pystatis.config import load_config
from pystatis.custom_exceptions import DestatisStatusError

logger = logging.getLogger(__name__)

JOB_ID_PATTERN = re.compile(r"\d+-\d+_\d+")
JOB_TIMEOUT = 60


def load_data(
    endpoint: str, method: str, params: dict, as_json: bool = False
) -> Union[str, dict]:
    """Load data identified by endpoint, method and params.

    Either load data from cache (previous download) or from Destatis.

    Args:
        endpoint (str): The endpoint for this data request.
        method (str): The method for this data request.
        params (dict): The dictionary holding the params for this data request.
        as_json (bool, optional): If True, result will be parsed as JSON. Defaults to False.

    Returns:
        Union[str, dict]: The data as raw text or JSON dict.
    """
    config = load_config()
    cache_dir = Path(config["DATA"]["cache_dir"])
    name = params.get("name")

    if name is not None:
        name = normalize_name(name)

    if endpoint == "data":
        if hit_in_cash(cache_dir, name, params):
            data = read_from_cache(cache_dir, name, params)
        else:
            response = get_data_from_endpoint(endpoint, method, params)
            data = response.text

            # status code 98 means that the table is too big
            # we have to start a job and wait for it to be ready
            response_status_code = 200
            try:
                # test for job-relevant status code
                response_status_code = response.json().get("Status").get("Code")
            except json.decoder.JSONDecodeError:
                pass

            if response_status_code == 98:
                job_response = start_job(endpoint, method, params)
                job_id = get_job_id_from_response(job_response)
                data = get_data_from_resultfile(job_id)

            cache_data(cache_dir, name, params, data)
    else:
        response = get_data_from_endpoint(endpoint, method, params)
        data = response.text

    if as_json:
        parsed_data: dict = json.loads(data)
        return parsed_data
    else:
        return data


def get_data_from_endpoint(
    endpoint: str, method: str, params: dict
) -> requests.Response:
    """
    Wrapper method which constructs an url for querying data from Destatis and
    sends a GET request.

    Args:
        endpoint (str): Destatis endpoint (eg. data, catalogue, ..)
        method (str): Destatis method (eg. cube, tablefile, ...)
        params (dict): dictionary of query parameters

    Returns:
        requests.Response: the response object holding the response from calling the Destatis endpoint.
    """
    config = load_config()
    url = f"{config['GENESIS API']['base_url']}{endpoint}/{method}"

    # params is used to calculate hash for caching so don't alter params dict here!
    params_ = params.copy()
    params_.update(
        {
            "username": config["GENESIS API"]["username"],
            "password": config["GENESIS API"]["password"],
        }
    )

    response = requests.get(url, params=params_, timeout=(5, 15))

    response.encoding = "UTF-8"
    _check_invalid_status_code(response)
    _check_invalid_destatis_status_code(response)

    return response


def start_job(endpoint: str, method: str, params: dict) -> requests.Response:
    """Small helper function to start a job in the background.

    Args:
        endpoint (str): Destatis endpoint (eg. data, catalogue, ..)
        method (str): Destatis method (eg. cube, tablefile, ...)
        params (dict): dictionary of query parameters

    Returns:
        requests.Response: the response object holding the response from calling the Destatis endpoint.
    """
    logger.warning(
        "Die Tabelle ist zu groß, um direkt abgerufen zu werden. Es wird eine Verarbeitung im Hintergrund gestartet."
    )
    params["job"] = "true"

    # starting a job
    response = get_data_from_endpoint(
        endpoint=endpoint, method=method, params=params
    )

    return response


def get_job_id_from_response(response: requests.Response) -> str:
    """Get the job ID of a successful started job.

    Args:
        response (requests.Response): Response from endpoint request with job set equal to true.

    Returns:
        str: the job id.
    """
    # check out job_id & inform user
    content = ""
    try:
        content = response.json().get("Status").get("Content")
    except json.JSONDecodeError:
        pass

    match_result = JOB_ID_PATTERN.search(content)
    job_id = match_result.group() if match_result is not None else ""

    return job_id


def get_data_from_resultfile(job_id: str) -> str:
    """Get data from a job once it is finished or when the timeout is reached.

    Args:
        job_id (str): Job ID generated by Destatis API.

    Returns:
        str: The raw data of the table file as returned by Destatis.
    """
    params = {
        "selection": "*" + job_id,
        "searchcriterion": "code",
        "sortcriterion": "code",
        "type": "all",
    }

    time_ = time.perf_counter()

    while (time.perf_counter() - time_) < JOB_TIMEOUT:
        response = get_data_from_endpoint(
            endpoint="catalogue", method="jobs", params=params
        )

        jobs = response.json().get("List")
        if len(jobs) > 0 and jobs[0].get("State") == "Fertig":
            break

        time.sleep(5)
    else:
        return ""

    params = {
        "name": job_id,
        "area": "all",
        "compress": "false",
        "format": "ffcsv",
    }
    response = get_data_from_endpoint(
        endpoint="data", method="resultfile", params=params
    )
    return str(response.text)


def _check_invalid_status_code(response: requests.Response) -> None:
    """
    Helper method which handles the status code from the response

    Args:
        response (requests.Response): The response object from the request

    Raises:
        AssertionError: Assert that status is not 4xx or 5xx
    """
    if response.status_code // 100 in [4, 5]:
        try:
            body: dict = response.json()
        except json.JSONDecodeError:
            body = {}

        content = body.get("Content")
        code = body.get("Code")
        logger.error("Error Code: %s. Content: %s.", code, content)
        raise requests.exceptions.HTTPError(
            f"The server returned a {response.status_code} status code."
        )


def _check_invalid_destatis_status_code(response: requests.Response) -> None:
    """
    Helper method which handles the status code returned from Destatis
    (if exists)

    Args:
        response (requests.Response): The response object from the request

    """
    try:
        response_dict = response.json()
    # catch possible errors raised by .json() (and only .json())
    except (
        UnicodeDecodeError,
        json.decoder.JSONDecodeError,
        requests.exceptions.JSONDecodeError,
    ):
        response_dict = None

    if response_dict is not None:
        _check_destatis_status(response_dict.get("Status", {}))


def _check_destatis_status(destatis_status: dict) -> None:
    """
    Helper method which checks the status message from Destatis.
    If the status message is erroneous an error will be raised.

    Possible Codes (2.1.2 Grundstruktur der Responses):
    # TODO: Ask Destatis for full list of error codes
    - 0: "erfolgreich" (Type: "Information")
    - 22: "erfolgreich mit Parameteranpassung" (Type: "Warnung")
    - 104: "Kein passendes Objekt zu Suche" (Type: "Information")

    Args:
        destatis_status (dict): Status response dict from Destatis

    Raises:
        DestatisStatusError: If the status code or type displays an error (caused by the user inputs)
    """
    # -1 status code for unexpected errors and if no status code is given (faulty response)
    destatis_status_code = destatis_status.get("Code", -1)
    destatis_status_type = destatis_status.get("Type", "Information")
    destatis_status_content = destatis_status.get("Content")

    # define status types
    error_en_de = ["Error", "Fehler"]
    warning_en_de = ["Warning", "Warnung"]

    # check for generic/ system error
    if destatis_status_code == -1:
        raise DestatisStatusError(destatis_status_content)

    # check for destatis/ query errors
    elif (destatis_status_code == 104) or (destatis_status_type in error_en_de):
        if destatis_status_code == 98:
            pass
        else:
            raise DestatisStatusError(destatis_status_content)

    # output warnings to user
    elif (destatis_status_code == 22) or (
        destatis_status_type in warning_en_de
    ):
        logger.warning(destatis_status_content)

    # output information to user
    elif destatis_status_type.lower() == "information":
        logger.info(
            "Code %d: %s", destatis_status_code, destatis_status_content
        )
