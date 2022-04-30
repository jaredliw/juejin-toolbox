from time import time
from typing import List
from urllib.parse import urljoin

from jwt import decode
from requests import post, RequestException, get


class JuejinError(RequestException):
    """Raised when Juejin returns a status code other than 200 OK."""
    pass


class JuejinGameSession:
    """Juejin game session."""
    BASE_URL = "https://juejin-game.bytedance.com/game/num-puzz/ugc/"
    GET_TOKEN_URL = "https://juejin.cn/get/token"

    def __init__(self, session_id: str):
        self.SESSION_ID = session_id
        self.TOKEN = self.__get_token_from_session_id()
        self.UID = self.__get_uid_from_token()
        self.HEADERS = {
            "authorization": "Bearer " + self.TOKEN
        }
        self.PARAMS = {
            "uid": self.UID,
            "time": int(time() * 1000)  # Millisecond timestamp
        }

    def __get_token_from_session_id(self) -> str:
        response = get(self.GET_TOKEN_URL, cookies={
            "sessionid": self.SESSION_ID
        }).json()
        try:
            return response["data"]
        except:
            raise JuejinError(response["err_msg"]) from None  # Suppress the context being printed

    def __get_uid_from_token(self) -> str:
        # Token is base64 encoded, UID is in it
        # Be aware of padding error
        # Extra '=' will be omitted
        try:
            return decode(self.TOKEN, options={"verify_signature": False})["userId"]
        except:
            raise ValueError("invalid token")

    def __post_request_handler(self, url_path: str, data: dict | None = None) -> dict:
        if data is None:
            data = {}

        response = post(urljoin(self.BASE_URL, url_path),
                        headers=self.HEADERS,
                        params=self.PARAMS,
                        json=data).json()
        try:
            return response["data"]
        except KeyError:
            # Suppress the context being printed
            raise JuejinError(response["message"]) from None

    def fetch_level_data(self) -> dict:
        return self.__post_request_handler("start")

    def submit_level(self, commands: List[list]) -> dict:
        return self.__post_request_handler("complete", {
            "command": commands
        })
