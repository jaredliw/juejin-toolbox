from requests import Session
from requests.exceptions import JSONDecodeError

from __init__ import JuejinError


class JuejinSession:
    """Juejin session."""

    def __init__(self, session_id: str):
        self.__session = Session()
        self.session.cookies.set("sessionid", session_id)

    @property
    def session(self):
        return self.__session

    def _request_handler(self, wrapped=None, *, return_keys=("data",), method="get"):

        def _decorator(f):
            def _wrapper(*args, **kwargs):
                result = f(*args, **kwargs)

                if isinstance(result, str):
                    url = result
                    req_config = {}
                elif isinstance(result, tuple):
                    if len(result) != 2:
                        raise ValueError(f"expect 1 to 2 return values, but got {len(result)}")
                    if not isinstance(result[0], str):
                        raise ValueError("first return value must be an url")
                    if not isinstance(result[1], dict):
                        raise ValueError("second return value (optional) must be a dict")
                    url = result[0]
                    req_config = result[1]
                else:
                    raise ValueError("a return value of url is required")

                if len(result) == 2:
                    if not isinstance(result[1], dict):
                        raise ValueError("second return value must be a dict if present")
                    req_config = result[1]

                ret = self.__session.request(method, url, **req_config)

                try:
                    ret_json = ret.json()
                except JSONDecodeError:
                    raise JuejinError(ret.text) from None

                if ret_json["err_msg"] != "success":
                    raise JuejinError(f"error {ret_json['err_no']}: "
                                      f"{ret_json['err_msg'] if ret_json['err_msg'] else '<no message>'}")

                if len(return_keys) == 1:
                    return ret_json[return_keys[0]]
                ret_list = []
                for key in return_keys:
                    ret_list.append(ret_json[key])
                return ret_list

            return _wrapper

        if wrapped:
            return _decorator(wrapped)
        else:
            return _decorator

    def is_checked_in(self) -> bool:
        """Get check in status.

        :return: True if checked in, False otherwise
        :rtype: bool
        """

        @self._request_handler
        def _inner():
            return "https://api.juejin.cn/growth_api/v1/get_today_status"

        return _inner()

    def check_in(self) -> dict:
        """Check in."""

        @self._request_handler(method="POST")
        def _inner():
            return "https://api.juejin.cn/growth_api/v1/check_in"

        return _inner()
