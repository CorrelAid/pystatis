from pystatis import __version__
import subprocess


def test_version():
    assert (
        __version__
        == subprocess.check_output(["poetry", "version"], text=True)
        .strip()
        .split()[-1]
    )
