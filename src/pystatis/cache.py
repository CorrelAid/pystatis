"""Module provides functions/decorators to cache downloaded data as well as remove cached data."""

import hashlib
import json
import logging
import re
import shutil
import zipfile
from datetime import date
from operator import attrgetter
from pathlib import Path
from typing import Optional

from pystatis import config
from pystatis.types import ParamDict

logger = logging.getLogger(__name__)

JOB_ID_PATTERN = r"_\d+"


def cache_data(
    cache_dir: str,
    name: Optional[str],
    params: ParamDict,
    data: bytes,
    content_type: str,
) -> None:
    """Compress and archive data within the configured cache directory.

    Data will be stored in a zip file within the cache directory.
    The folder structure will be `<name>/<endpoint>/<method>/<hash(params)>`.
    This allows to cache different results for different params.

    Args:
        cache_dir (str): The cash directory as configured in the config.
        name (str): The unique identifier in GENESIS-Online.
        params (dict): The dictionary holding the params for this data request.
        data (bytes): The raw bytes content of the response from GENESIS-Online.
        content_type (str): The content type of the data, e.g. "csv" or "zip".
    """
    # pylint: disable=too-many-arguments
    if name is None or content_type not in ["csv", "zip"]:
        return

    data_dir = _build_file_path(cache_dir, name, params)
    file_name = f"{str(date.today()).replace('-', '')}.{content_type}"
    file_path = data_dir / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if content_type in ["csv"]:
        # we have to first save the content to a text file, before we can add it to a
        #   compressed archive, and finally have to delete the file so only the archive remains
        with open(file_path, "wb") as file:
            file.write(data)

        with zipfile.ZipFile(
            str(file_path).replace(f".{content_type}", ".zip"),
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as myzip:
            myzip.write(file_path, arcname=file_name)

        file_path.unlink()

    elif content_type == "zip":
        with open(file_path, "wb") as file:
            file.write(data)

    logger.info("Data was successfully cached under %s.", file_path)


def read_from_cache(
    cache_dir: str,
    name: Optional[str],
    params: ParamDict,
) -> bytes:
    """Read and return compressed data from cache.

    Args:
        cache_dir (str): The cash directory as configured in the config.
        name (str): The unique identifier in GENESIS-Online.
        params (dict): The dictionary holding the params for this data request.

    Returns:
        bytes: The uncompressed raw text data as bytes.
    """
    if name is None:
        return bytes()

    data_dir = _build_file_path(cache_dir, name, params)

    latest_version = sorted(
        data_dir.glob("*"),
        key=attrgetter("stem"),
    )[-1]
    file_name = latest_version.name
    file_path = data_dir / file_name
    with zipfile.ZipFile(file_path, "r") as zipfile_:
        single_file = zipfile_.filelist[0].filename
        data = zipfile_.read(single_file)

    return data


def _build_file_path(cache_dir: str, name: str, params: ParamDict) -> Path:
    """Builds a unique cache directory name from name and hashed params dictionary.

    The way this method works is that it creates a path under cache dir that is unique
    because the name is a unique EVAS identifier number in Destatis and the hash is
    (close enough) unique to a given dictionary with query parameter values.

    Args:
        cache_dir (str): The root cache directory as configured in the config.ini.
        name (str): The unique identifier for an object in Destatis.
        params (dict): The query parameters for a given call to the Destatis API.

    Returns:
        Path: The path object to the directory where the data will be downloaded/cached.
    """
    params_ = params.copy()
    # we have to delete the job key here because otherwise we will not have a cache hit
    # we use 10 digits because this is enough security to avoid hash collisions
    if "job" in params_:
        del params_["job"]

    params_hash = hashlib.blake2s(digest_size=10, usedforsecurity=False)
    params_hash.update(json.dumps(params_).encode("UTF-8"))

    data_dir = Path(cache_dir) / name / params_hash.hexdigest()

    return data_dir


def normalize_name(name: str) -> str:
    """Normalize a Destatis object name by omitting the optional job id.

    Args:
        name (str): The unique identifier in GENESIS-Online.

    Returns:
        str: The unique identifier without the optional job id.
    """
    if re.findall(JOB_ID_PATTERN, name):
        name = name.split("_")[0]

    return name


def hit_in_cash(
    cache_dir: str,
    name: Optional[str],
    params: ParamDict,
) -> bool:
    """Check if data is already cached.

    Args:
        cache_dir (str): The cash directory as configured in the config.
        name (str): The unique identifier in GENESIS-Online.
        params (dict): The dictionary holding the params for this data request.

    Returns:
        bool: True, if combination of name, endpoint, method and params is already cached.
    """
    if name is None:
        return False

    data_dir = _build_file_path(cache_dir, name, params)
    return data_dir.exists()


def clear_cache(name: Optional[str] = None) -> None:
    """Clean the data cache completely or just a specified name.

    Args:
        name (str, optional): Unique name to be deleted from cached data.
    """
    cache_dir = Path(config.get_cache_dir())

    # remove specified file (directory) from the data cache
    # or clear complete cache (remove childs, preserve base)
    file_paths = [cache_dir / name] if name is not None else list(cache_dir.iterdir())

    for file_path in file_paths:
        # delete if file or symlink, otherwise remove complete tree
        try:
            if file_path.is_file() or file_path.is_symlink():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
        except (OSError, ValueError, FileNotFoundError) as e:
            logger.warning("Failed to delete %s. Reason: %s", file_path, e)

        logger.info("Removed files: %s", file_paths)
