from typing import Dict, List, Union

from src.check_in.api import JuejinSession


class Lottery:
    def __init__(self, juejin_session: JuejinSession):
        self.session = juejin_session

    def get_config(self) -> Dict[str, Union[List[Dict[str, str]], int]]:
        """Get lottery config.

        :return: ID, name, type, image, and unlock count of every prize, the cost of a draw and the number of free draw.
        :rtype: Dict[str, Union[List[Dict[str, str]], int]]
        """

        @self.session._request_handler
        def _inner():
            return "https://api.juejin.cn/growth_api/v1/lottery_config/get"

        return _inner()

    def get_history(self) -> dict:
        """Get lottery history.

        :return: User ID, history ID, username, user avatar, prize name, prize image and date of every record.
        :rtype: Dict[str, List[Dict[str, str]]]
        """

        @self.session._request_handler(method="POST")
        def _inner():
            return "https://api.juejin.cn/growth_api/v1/lottery_history/global_small"

        return _inner()

    def draw(self) -> Dict[str, str]:
        """Draw lottery.

        :return: ID, lottery ID, name, type, image, description, history ID and luck of the draw.
        :rtype: Dict[str, str]
        """

        @self.session._request_handler(method="POST")
        def _inner():
            return "https://api.juejin.cn/growth_api/v1/lottery/draw"

        return _inner()

    def get_luck(self) -> Dict[str, Union[str, int]]:
        """Get luck; when the value of luck reaches 6000, you will win a Juejin merch!

        :return: ID, user ID and luck.
        ::rtype: Dict[str, Union[str, int]]
        """

        @self.session._request_handler(method="POST")
        def _inner():
            return "https://api.juejin.cn/growth_api/v1/lottery_lucky/my_lucky"

        return _inner()

    def attract_luck(self, lottery_history_id: str) -> Dict[str, Union[int, bool]]:
        """Attract luck from others who had won a prize. You can do this at most once a day.

        :param lottery_history_id: ID of the record you want to attract luck from.
        :type lottery_history_id: str
        :return: Your luck and the luck you have attracted.
        ::rtype: Dict[str, Union[int, bool]]
        """

        @self.session._request_handler(method="POST")
        def _inner():
            return "https://api.juejin.cn/growth_api/v1/lottery_lucky/dip_lucky", \
                   {
                       "json": {
                           "lottery_history_id": lottery_history_id
                       }
                   }

        return _inner()
