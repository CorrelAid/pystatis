import subprocess

from docs.source.conf import release
from pystatis import __version__


def test_version():
    assert (
        __version__
        == subprocess.check_output(["poetry", "version"], text=True)
        .strip()
        .split()[-1]
    )


def test_docs_version():
    assert __version__ == release
