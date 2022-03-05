from base64 import b64decode
from re import search
from time import time

from requests import post, RequestException

URL = "https://juejin-game.bytedance.com/game/num-puzz/ugc/start"


class JuejinError(RequestException):
    """Raised when Juejin returns a status code other than 200 OK."""
    pass


def fetch_data(authorization: str) -> dict:
    """Fetch game data from Juejin.

    :param authorization: User's Bearer Token
    :type authorization: str
    :return: data in JSON format
    :rtype: dict
    """
    # token is base64 encoded, UID is in it
    # Be aware of padding error
    decoded_token = str(b64decode(authorization.removeprefix("Bearer ") + "=="))  # extra '=' will be omitted
    response = post(URL, headers={
        "authorization": authorization
    }, params={
        "uid": search(r'(?<="userId":")\d*', decoded_token)[0],  # Search for UID in token
        "time": time() * 1000  # Millisecond timestamp
    }).json()
    try:
        return response["data"]
    except KeyError:
        raise JuejinError(response["message"]) from None  # Suppress the context being printed
