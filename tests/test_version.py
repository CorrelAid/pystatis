import subprocess

from pystatis import __version__


def test_version():
    assert __version__ == subprocess.check_output(["poetry", "version"], text=True).strip().split()[-1]
