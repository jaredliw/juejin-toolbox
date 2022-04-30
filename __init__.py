from os import environ

from requests import RequestException

session_id = environ["JUEJIN_SESSION_ID"]
if not session_id:
    raise ValueError("environment variable 'JUEJIN_SESSION_ID' is not set")


class JuejinError(RequestException):
    """Raised when Juejin returns a status code other than 200 OK."""
    pass
