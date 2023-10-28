import re
from pathlib import Path

import pytest

from pystatis.cache import (
    _build_file_path,
    cache_data,
    clear_cache,
    hit_in_cash,
    normalize_name,
    read_from_cache,
)
from pystatis.config import get_cache_dir, init_config


@pytest.fixture()
def cache_dir(tmp_path_factory):
    # remove white-space and non-latin characters (issue fo some user names)
    temp_dir = str(tmp_path_factory.mktemp(".pystatis"))
    temp_dir = re.sub(r"[^\x00-\x7f]", r"", temp_dir.replace(" ", ""))

    init_config(temp_dir)

    return get_cache_dir()


@pytest.fixture(scope="module")
def params():
    return {"name": "test-cache", "area": "all"}


def test_build_file_path(cache_dir, params):
    data_dir = _build_file_path(cache_dir, "test-build-file-path", params)

    assert isinstance(data_dir, Path)
    assert data_dir.parent == Path(cache_dir) / "test-build-file-path"
    assert data_dir.name.isalnum()


def test_cache_data(cache_dir, params):
    assert len(list((Path(cache_dir) / "data").glob("*"))) == 0

    test_data = "test"
    cache_data(cache_dir, "test-cache-data", params, test_data)

    data_dir = _build_file_path(cache_dir, "test-cache-data", params)

    assert data_dir.exists() and len(list(data_dir.glob("*.zip"))) == 1


def test_read_from_cache(cache_dir, params):
    test_data = "test read from cache"
    cache_data(
        cache_dir,
        "test-read-cache",
        params,
        test_data,
    )
    data = read_from_cache(cache_dir, "test-read-cache", params)

    assert data == test_data


def test_hit_cache(cache_dir, params):
    assert not hit_in_cash(cache_dir, "test-hit-cache", params)
    cache_data(cache_dir, "test-hit-cache", params, "test")
    assert hit_in_cash(cache_dir, "test-hit-cache", params)


def test_normalize_name():
    full_name = "42153-0001_878150652"
    assert normalize_name(full_name) == "42153-0001"


def test_change_in_params(cache_dir, params):
    params_ = params.copy()

    name = "test-change-in-params"
    assert not hit_in_cash(cache_dir, name, params_)
    cache_data(cache_dir, name, params_, "test")
    assert hit_in_cash(cache_dir, name, params_)

    params_.update({"new-param": 2})
    assert not hit_in_cash(cache_dir, name, params_)


def test_ignore_jobs_in_params(cache_dir, params):
    params_ = params.copy()

    name = "test-ignore-jobs"
    cache_data(cache_dir, name, params_, "test")

    params_.update({"job": True})
    assert hit_in_cash(cache_dir, name, params_)

    params_.update({"job": False})
    assert hit_in_cash(cache_dir, name, params_)


def test_clean_cache(cache_dir, params):
    name = "test-clean-cache"
    cache_data(cache_dir, name, params, "test")

    data_dir = _build_file_path(cache_dir, name, params)
    cached_data_file = list(data_dir.glob("*.zip"))[0]

    assert cached_data_file.exists() and cached_data_file.is_file()

    clear_cache(name=name)

    assert not cached_data_file.exists() and not cached_data_file.is_file()
