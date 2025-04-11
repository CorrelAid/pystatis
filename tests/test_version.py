import tomllib
from pathlib import Path

from pystatis import __version__


def test_version():
    # Read version from pyproject.toml
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    # Get version from project metadata
    project_version = pyproject_data["project"]["version"]

    assert __version__ == project_version
