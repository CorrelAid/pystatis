import zipfile
from pathlib import Path

import pytest

from pystatis.table import Table


@pytest.fixture
def easy_raw_data():
    with zipfile.ZipFile(Path(__file__).parent / "rsc" / "data.zip") as myzip:
        with myzip.open("12411BJ001.txt", "r") as file:
            return file.read().decode()


@pytest.fixture
def hard_raw_data():
    with zipfile.ZipFile(Path(__file__).parent / "rsc" / "data.zip") as myzip:
        with myzip.open("22922KJ1141.txt", "r") as file:
            return file.read().decode()


@pytest.fixture
def raw_data():
    with zipfile.ZipFile(Path(__file__).parent / "rsc" / "data.zip") as myzip:
        with myzip.open("11111-0001_flat.csv", "r") as file:
            return file.read().decode(encoding="latin-1")


@pytest.mark.parametrize(
    "raw_data, expected_shape",
    [
        (
            "raw_data",
            (17, 10),
        ),
    ],
    indirect=["raw_data"],
)
def test_get_data(
    mocker,
    raw_data,
    expected_shape,
):
    # mock load_data API calls
    metadata_dict = {"metadata": "json_response_dict"}
    mocker.patch(
        "pystatis.table.load_data", side_effect=[raw_data, metadata_dict]
    )

    # create instance with dummy name
    table_class = Table(name="dummy_name")

    # run get data function
    table_class.get_data()

    # general variables
    assert table_class.name == "dummy_name"
    assert table_class.raw_data == raw_data

    # data (table)
    assert table_class.data.shape == expected_shape

    # metadata
    assert table_class.metadata == metadata_dict
