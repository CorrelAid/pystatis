"""Define custom "speaking" Exception and Error classes."""


class DestatisStatusError(ValueError):
    """Raised when Destatis status code indicates an error ("Fehler")"""

    pass


class PystatisConfigError(Exception):
    """Raised when pystatis configuration is invalid."""

    pass


class QueryParameterError(Exception):
    """Raised when invalid query parameters are passed."""

    pass
