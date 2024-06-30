"""Define custom "speaking" Exception and Error classes."""


class DestatisStatusError(ValueError):
    """Raised when Destatis status code indicates an error ("Fehler")"""

    pass


class PystatisConfigError(Exception):
    """Raised when pystatis configuration is invalid."""

    pass


class NoNewerDataError(Exception):
    """Raised when no newer data is available for download (parameter stand, API Error Code 50)."""

    pass
