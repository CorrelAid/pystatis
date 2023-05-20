from docs.source.conf import release
from pystatis import __version__


def test_version():
    assert __version__ == "0.1.4"


def test_docs_version():
    assert __version__ == release
