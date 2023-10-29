"""Define custom "speaking" Exception and Error classes."""


class DestatisStatusError(ValueError):
    """Raised when Destatis status code indicates an error ("Fehler")"""

    pass


class PystatisConfigError(Exception):
    """Raised when pystatis configuration is invalid."""

    pass
