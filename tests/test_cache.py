import shutil
from configparser import RawConfigParser
from pathlib import Path

import pytest

from pystatis import config
from pystatis.cache import (
    _build_file_path,
    cache_data,
    clear_cache,
    hit_in_cash,
    normalize_name,
    read_from_cache,
)


@pytest.fixture()
def config_() -> RawConfigParser:
    old_config = config.load_config()
    config.delete_config()
    yield config.config
    config.config = old_config
    config.write_config()


@pytest.fixture()
def cache_dir(config_) -> str:
    old_cache_dir = config.get_cache_dir()
    config_.set(
        "data",
        "cache_dir",
        str(Path(config.DEFAULT_CONFIG_DIR) / "test-cache-dir"),
    )
    cache_dir = config.get_cache_dir()
    yield cache_dir
    config_.set("data", "cache_dir", old_cache_dir)
    if Path(cache_dir).exists():
        # delete cache dir
        shutil.rmtree(cache_dir)


@pytest.fixture(scope="module")
def params():
    return {"name": "test-cache", "area": "all"}


def test_build_file_path(cache_dir, params):
    data_dir = _build_file_path(cache_dir, "test-build-file-path", params)

    assert isinstance(data_dir, Path)
    assert data_dir.parent == Path(cache_dir) / "test-build-file-path"
    assert data_dir.name.isalnum()


def test_cache_data(cache_dir, params):
    assert len(list(Path(cache_dir).glob("*"))) == 0

    test_data = "test".encode()
    cache_data(cache_dir, "test-cache-data", params, test_data, "csv")

    data_dir = _build_file_path(cache_dir, "test-cache-data", params)

    assert data_dir.exists() and len(list(data_dir.glob("*.zip"))) == 1


def test_read_from_cache(cache_dir, params):
    test_data = "test read from cache".encode()
    cache_data(cache_dir, "test-read-cache", params, test_data, "csv")
    data = read_from_cache(cache_dir, "test-read-cache", params)

    assert data == test_data


def test_hit_cache(cache_dir, params):
    assert not hit_in_cash(cache_dir, "test-hit-cache", params)
    cache_data(cache_dir, "test-hit-cache", params, "test".encode(), "csv")
    assert hit_in_cash(cache_dir, "test-hit-cache", params)


def test_normalize_name():
    full_name = "42153-0001_878150652"
    assert normalize_name(full_name) == "42153-0001"


def test_change_in_params(cache_dir, params):
    params_ = params.copy()

    name = "test-change-in-params"
    assert not hit_in_cash(cache_dir, name, params_)
    cache_data(cache_dir, name, params_, "test".encode(), "csv")
    assert hit_in_cash(cache_dir, name, params_)

    params_.update({"new-param": 2})
    assert not hit_in_cash(cache_dir, name, params_)


def test_ignore_jobs_in_params(cache_dir, params):
    params_ = params.copy()

    name = "test-ignore-jobs"
    cache_data(cache_dir, name, params_, "test".encode(), "csv")

    params_.update({"job": True})
    assert hit_in_cash(cache_dir, name, params_)

    params_.update({"job": False})
    assert hit_in_cash(cache_dir, name, params_)


def test_clean_cache(cache_dir, params):
    name = "test-clean-cache"
    cache_data(cache_dir, name, params, "test".encode(), "csv")

    data_dir = _build_file_path(cache_dir, name, params)
    cached_data_file = list(data_dir.glob("*.zip"))[0]

    assert cached_data_file.exists() and cached_data_file.is_file()

    clear_cache(name=name)

    assert not cached_data_file.exists() and not cached_data_file.is_file()
