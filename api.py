from base64 import b64decode
from re import search
from time import time
from typing import List
from urllib.parse import urljoin

from requests import post, RequestException


class JuejinError(RequestException):
    """Raised when Juejin returns a status code other than 200 OK."""
    pass


class JuejinGameSession:
    """Juejin game session."""
    BASE_URL = "https://juejin-game.bytedance.com/game/num-puzz/ugc/"

    def __init__(self, token: str):
        self.__token = token
        self.__uid = self.__get_uid_from_token()
        self.__HEADERS = {
            "authorization": self.__token
        }
        self.__PARAMS = {
            "uid": self.__uid,
            "time": int(time() * 1000)  # Millisecond timestamp
        }

    def __get_uid_from_token(self) -> str:
        # token is base64 encoded, UID is in it
        # Be aware of padding error
        decoded_token = str(b64decode(self.__token.removeprefix("Bearer ") + "=="))  # extra '=' will be omitted
        search_result = search(r'(?<="userId":")\d*', decoded_token)  # Search for UID in token
        if search_result is None:
            raise ValueError("invalid token")
        return search_result[0]

    def __post_request_handler(self, url_path: str, data: dict | None = None) -> dict:
        if data is None:
            data = {}

        response = post(urljoin(self.BASE_URL, url_path),
                        headers=self.__HEADERS,
                        params=self.__PARAMS,
                        json=data).json()
        try:
            return response["data"]
        except KeyError:
            raise JuejinError(response["message"]) from None  # Suppress the context being printed

    def fetch_level_data(self) -> dict:
        return self.__post_request_handler("start")

    def submit_level(self, commands: List[list]) -> dict:
        return self.__post_request_handler("complete", {
            "originality": 0,
            "command": commands
        })
