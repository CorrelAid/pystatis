from docs.source.conf import release
from pystatis import __version__


def test_docs_version():
    # version hard-coded in docs, since pre-commit hook fails to import pystatis
    assert __version__ == release
