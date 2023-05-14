import zipfile
from pathlib import Path

import numpy as np
import pytest

from pystatis.cube import Cube, assign_correct_types, parse_cube, rename_axes


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
def easy_cube(easy_raw_data):
    return parse_cube(easy_raw_data)


@pytest.fixture
def hard_cube(hard_raw_data):
    return parse_cube(hard_raw_data)


@pytest.fixture
def raw_data(request, easy_raw_data, hard_raw_data):
    if request.param == "easy_cube":
        return easy_raw_data
    elif request.param == "hard_cube":
        return hard_raw_data


@pytest.fixture
def cube(request, easy_cube, hard_cube):
    if request.param == "easy_cube":
        return easy_cube
    elif request.param == "hard_cube":
        return hard_cube


@pytest.mark.parametrize(
    "raw_data, expected_shape, expected_DQ, expected_DQ_ERH, expected_DQA, expected_DQZ, expected_DQI,",
    [
        (
            "hard_cube",
            (19185, 13),
            "22922KJ114",
            "22922",
            ["KREISE", "GES", "ERW122", "ELGAT2"],
            "JAHR",
            ["ELG002", "ELG003"],
        ),
        (
            "easy_cube",
            (42403, 10),
            "12411BJ001",
            "12411",
            ["DINSG", "NAT", "GES", "FAMST8", "ALT013"],
            "STAG",
            ["BEVSTD"],
        ),
    ],
    indirect=["raw_data"],
)
def test_parse_cube(
    raw_data,
    expected_shape,
    expected_DQ,
    expected_DQ_ERH,
    expected_DQA,
    expected_DQZ,
    expected_DQI,
):
    cube = parse_cube(raw_data)

    assert isinstance(cube, dict)
    assert len(cube) == raw_data.count("K;")

    assert cube["QEI"].shape == expected_shape
    assert cube["DQ"]["FACH-SCHL"].values[0] == expected_DQ
    assert cube["DQ-ERH"]["FACH-SCHL"].values[0] == expected_DQ_ERH
    assert cube["DQA"]["NAME"].to_list() == expected_DQA
    assert cube["DQZ"]["NAME"].values[0] == expected_DQZ
    assert cube["DQI"]["NAME"].to_list() == expected_DQI


@pytest.mark.parametrize(
    "cube, expected_names",
    [
        (
            "easy_cube",
            [
                "DINSG",
                "NAT",
                "GES",
                "FAMST8",
                "ALT013",
                "STAG",
                "BEVSTD_WERT",
                "BEVSTD_QUALITAET",
                "BEVSTD_GESPERRT",
                "BEVSTD_WERT-VERFAELSCHT",
            ],
        ),
        (
            "hard_cube",
            [
                "KREISE",
                "GES",
                "ERW122",
                "ELGAT2",
                "JAHR",
                "ELG002_WERT",
                "ELG002_QUALITAET",
                "ELG002_GESPERRT",
                "ELG002_WERT-VERFAELSCHT",
                "ELG003_WERT",
                "ELG003_QUALITAET",
                "ELG003_GESPERRT",
                "ELG003_WERT-VERFAELSCHT",
            ],
        ),
    ],
    indirect=["cube"],
)
def test_rename_axes(cube, expected_names):
    cube = rename_axes(cube)

    assert list(cube["QEI"].columns) == expected_names


@pytest.mark.parametrize(
    "cube, test_cols, test_types",
    [
        (
            "easy_cube",
            [
                "BEVSTD_WERT",
            ],
            [np.integer],
        ),
        (
            "hard_cube",
            [
                "ELG002_WERT",
                "ELG003_WERT",
            ],
            [np.integer, np.integer],
        ),
    ],
    indirect=["cube"],
)
def test_rename_axes(cube, test_cols, test_types):
    cube = assign_correct_types(rename_axes(cube))

    for col, expected_type in zip(test_cols, test_types):
        assert issubclass(cube["QEI"][col].dtype.type, expected_type)


@pytest.mark.parametrize(
    "raw_data, expected_shape, test_cols, test_types",
    [
        (
            "hard_cube",
            (19185, 13),
            [
                "ELG002_WERT",
                "ELG003_WERT",
            ],
            [np.integer, np.integer],
        ),
        (
            "easy_cube",
            (42403, 10),
            [
                "BEVSTD_WERT",
            ],
            [np.integer],
        ),
    ],
    indirect=["raw_data"],
)
def test_get_data(
    mocker,
    raw_data,
    expected_shape,
    test_cols,
    test_types,
):
    # mock load_data API calls
    metadata_dict = {"metadata": "json_response_dict"}
    mocker.patch(
        "pystatis.cube.load_data", side_effect=[raw_data, metadata_dict]
    )

    # create instance with dummy name
    cube_class = Cube(name="dummy_name")

    # run get data function
    cube_class.get_data()

    # general variables
    assert cube_class.name == "dummy_name"
    assert cube_class.raw_data == raw_data

    # cube and data
    assert isinstance(cube_class.cube, dict)
    assert len(cube_class.cube) == raw_data.count("K;")

    for col, expected_type in zip(test_cols, test_types):
        assert issubclass(cube_class.cube["QEI"][col].dtype.type, expected_type)

    assert cube_class.data.shape == expected_shape

    # metadata
    assert cube_class.metadata == metadata_dict
