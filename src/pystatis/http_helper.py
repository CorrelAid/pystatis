"""Wrapper module for the data endpoint."""

import json
import logging
import re
import time

import requests

from pystatis import cache, config, db
from pystatis.exception import DestatisStatusError, NoNewerDataError, TableNotFoundError
from pystatis.types import ParamDict

logger = logging.getLogger(__name__)

JOB_ID_PATTERN = re.compile(r"(?<=:\s).*_\d+")
JOB_TIMEOUT = 3000


def load_data(
    endpoint: str,
    method: str,
    params: ParamDict,
    db_name: str | None = None,
) -> bytes:
    """Load data identified by endpoint, method and params.

    Either load data from cache (previous download) or from Destatis.
    If no database is given, params has to have a valid value for "name" key.

    Args:
        endpoint (str): The endpoint for this data request.
        method (str): The method for this data request.
        params (dict): The dictionary holding the params for this data request.
        db_name (str, optional): The database to use for this data request.
            One of "genesis", "zensus", "regio". Defaults to None.

    Returns:
        bytes: The response content as bytes data.
    """
    cache_dir = config.get_cache_dir()
    name = params.get("name")

    if name is not None:
        name = cache.normalize_name(name)

    if endpoint == "data":
        if cache.hit_in_cash(cache_dir, name, params):
            data = cache.read_from_cache(cache_dir, name, params)
            logger.info("Data was loaded from cache.")
        else:
            response = get_data_from_endpoint(endpoint, method, params, db_name)
            content_type = response.headers.get("Content-Type", "text/csv").split("/")[-1]
            data = response.content

            # status code 98 means that the table is too big
            # we have to start a job and wait for it to be ready
            response_status_code = 200
            try:
                # test for job-relevant status code
                response_status_code = response.json().get("Status").get("Code")
            except (json.decoder.JSONDecodeError, requests.exceptions.JSONDecodeError):
                pass

            if response_status_code == 98:
                job_response = start_job(endpoint, method, params)
                job_id = get_job_id_from_response(job_response)
                logger.warning(
                    "Verarbeitung im Hintergrund erfolgreich gestartet. Job-ID: %s.",
                    job_id,
                )
                response = get_data_from_resultfile(job_id, params, db_name)
                assert isinstance(response.content, bytes)  # nosec assert_used
                content_type = response.headers.get("Content-Type", "text/csv").split("/")[-1]
                data = response.content

            cache.cache_data(cache_dir, name, params, data, content_type)

            # bytes response in case of zip content type cannot be directly decoded, so we have to load the zip first!
            if content_type == "zip":
                data = cache.read_from_cache(cache_dir, name, params)
    else:
        response = get_data_from_endpoint(endpoint, method, params, db_name)
        data = response.content

    return data


def get_data_from_endpoint(
    endpoint: str, method: str, params: ParamDict, db_name: str | None = None
) -> requests.Response:
    """
    Wrapper method which constructs a url for querying data from Destatis and
    sends a GET request.

    Args:
        endpoint (str): Destatis endpoint (eg. data, catalogue, ..)
        method (str): Destatis method (eg. tablefile, ...)
        params (dict): dictionary of query parameters
        db_name (str, optional): The database to use for this data request.
            One of "genesis", "zensus", "regio". Defaults to None.

    Returns:
        requests.Response: the response object holding the response from calling the Destatis endpoint.
    """

    def get_response(db_name: str, params: ParamDict) -> requests.Response:
        db_host, db_user, db_pw = db.get_settings(db_name)
        url = f"{db_host}{endpoint}/{method}"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "username": db_user,
            "password": db_pw,
        }

        return requests.post(url, headers=headers, data=params, timeout=(30, 300))

    # Determine database by matching regex to item code
    if db_name is None:
        table_name = params.get("name", params.get("selection", ""))

        db_matches = db.identify_db_matches(table_name)
        db_name = db.select_db_by_credentials(db_matches)
        logger.info("Database selected: %s", db_name)

    # params is used to calculate hash for caching so don't alter params dict here!
    try:
        response = get_response(db_name, params)
    except requests.exceptions.Timeout as tout:
        logger.error(
            "Initial request against %s/%s timed out after %s minutes. "
            "Probably a problem with the API. "
            "You can try again later or use the web interface.",
            endpoint,
            method,
            300 // 60,
        )
        raise SystemExit(1) from tout

    response.encoding = "UTF-8"
    _check_invalid_status_code(response)

    # logincheck endpoint only returns string status with failure/success information. No further check necessary.
    if method != "logincheck":
        _check_invalid_destatis_status_code(response)

    return response


def start_job(endpoint: str, method: str, params: ParamDict) -> requests.Response:
    """Small helper function to start a job in the background.

    Args:
        endpoint (str): Destatis endpoint (eg. data, catalogue, ..)
        method (str): Destatis method (eg. tablefile, ...)
        params (dict): Dictionary of query parameters.

    Returns:
        requests.Response: the response object holding the response from calling the Destatis endpoint.
    """
    logger.warning(
        "Die Tabelle ist zu groß, um direkt abgerufen zu werden. Es wird eine Verarbeitung im Hintergrund gestartet."
    )
    job_params = params.copy()
    job_params["job"] = "true"

    # starting a job
    response = get_data_from_endpoint(endpoint=endpoint, method=method, params=job_params)

    return response


def get_job_id_from_response(response: requests.Response) -> str:
    """Get the job ID of a successfully started job.

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


def get_data_from_resultfile(
    job_id: str, params: ParamDict, db_name: str | None = None
) -> requests.Response:
    """Get data from a job once it is finished or when the timeout is reached.

    Args:
        job_id (str): Job ID generated by Destatis API.
        params (dict): Dictionary of query parameters.
        db_name (str, optional): The database to use for this data request.
            One of "genesis", "zensus", "regio". Defaults to None.

    Returns:
        requests.Response: the response object holding the response from calling the Destatis endpoint.
    """
    job_params = {
        "selection": job_id,
        "area": "user",
        "pagelength": "1",
    }

    time_ = time.perf_counter()

    while (time.perf_counter() - time_) < JOB_TIMEOUT:
        try:
            response = get_data_from_endpoint(
                endpoint="catalogue", method="results", params=job_params, db_name=db_name
            )

            jobs = response.json().get("List")
            if len(jobs) > 0:
                logger.info(
                    (
                        "Verarbeitung im Hintergrund abgeschlossen. "
                        "Ergebnis kann jetzt abgerufen werden über "
                        "/data/resultfile und Job-ID: %s."
                    ),
                    job_id,
                )
                break
        except DestatisStatusError:
            logger.info("Verarbeitung im Hintergrund läuft noch...")

        time.sleep(5)
    else:
        logger.error(
            "Verarbeitungsfenster von %s Minuten überschritten. Job-Datei konnte nicht heruntergeladen werden.",
            JOB_TIMEOUT // 60,
        )
        return bytes()

    params = params.copy()
    params["name"] = job_id
    response = get_data_from_endpoint(
        endpoint="data", method="resultfile", params=params, db_name=db_name
    )
    return response


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
            body = response.json()
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


def _check_destatis_status(destatis_status: dict) -> None:  # type: ignore
    """
    Helper method which checks the status message from Destatis.
    If the status message is erroneous an error will be raised.

    Possible Codes (2.1.2 Grundstruktur der Responses):
    # TODO: Ask Destatis for full list of error codes
    - 0: "erfolgreich" (Type: "Information")
    - 22: "erfolgreich mit Parameteranpassung" (Type: "Warnung")
    - 50: "Keine aktualisierten Daten vorhanden." (Type: "Information")
    - 90: "Die angeforderte Tabelle ist nicht vorhanden" (Type: "Information")
    - 104: "Kein passendes Objekt zu Suche" (Type: "Information")

    Args:
        destatis_status (dict): Status response dict from Destatis

    Raises:
        DestatisStatusError: If the status code or type displays an error (caused by the user inputs)
    """
    # Status codes
    STATUS_CODE_PARAM_ADJUSTED = 22
    STATUS_CODE_NO_NEW_DATA = 50
    STATUS_CODE_TABLE_NOT_FOUND = 90
    STATUS_CODE_LARGE_TABLE = 98
    STATUS_CODE_NO_MATCHING_OBJECT = 104
    STATUS_CODE_ERROR = -1  # For unexpected errors and if no status code is given

    # Status types
    STATUS_TYPE_INFORMATION = "Information"
    ERROR_TYPES = ["Error", "Fehler"]
    WARNING_TYPES = ["Warning", "Warnung"]

    destatis_status_code = destatis_status.get("Code", STATUS_CODE_ERROR)
    destatis_status_type = destatis_status.get("Type", STATUS_TYPE_INFORMATION)
    destatis_status_content = destatis_status.get("Content")

    # Check for generic/system error
    if destatis_status_code == STATUS_CODE_ERROR:
        raise DestatisStatusError(destatis_status_content)

    # Check for destatis/query errors
    elif (
        destatis_status_code
        in [STATUS_CODE_NO_MATCHING_OBJECT, STATUS_CODE_NO_NEW_DATA, STATUS_CODE_TABLE_NOT_FOUND]
    ) or (destatis_status_type in ERROR_TYPES):
        if destatis_status_code == STATUS_CODE_LARGE_TABLE:
            pass
        elif destatis_status_code == STATUS_CODE_NO_NEW_DATA:
            raise NoNewerDataError(destatis_status_content)
        elif destatis_status_code == STATUS_CODE_TABLE_NOT_FOUND:
            raise TableNotFoundError(destatis_status_content)
        else:
            raise DestatisStatusError(destatis_status_content)

    # Output warnings to user
    elif (destatis_status_code == STATUS_CODE_PARAM_ADJUSTED) or (
        destatis_status_type in WARNING_TYPES
    ):
        logger.warning(destatis_status_content)

    # Output information to user
    elif destatis_status_type.lower() == STATUS_TYPE_INFORMATION.lower():
        logger.info("Code %d: %s", destatis_status_code, destatis_status_content)
