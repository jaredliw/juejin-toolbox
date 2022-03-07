from base64 import b64decode
from copy import copy
from itertools import chain
from re import search
from time import time, sleep
from typing import List, Literal, Tuple, Union, Generator

from requests import post

VALID_OPERATIONS = ("+", "-", "*", "/", "&")
URL = "https://juejin-game.bytedance.com/game/num-puzz/ugc/start"


def calc(num1: int, sym: Literal["+", "-", "*", "/", "&"], num2: int) -> int:
    if not isinstance(num1, int) or not isinstance(num2, int) or sym not in VALID_OPERATIONS:
        raise TypeError(f"unsupported operand type(s) for {sym}: '{type(num1).__name__}' and '{type(num2).__name__}'")

    if sym == "+":
        return num1 + num2
    elif sym == "-":
        if num1 < num2:
            raise ArithmeticError(f"'{num1} {sym} {num2}': {num1} is smaller than {num2}")
        return num1 - num2
    elif sym == "*":
        return num1 * num2
    elif sym == "/":
        ans = num1 / num2
        if not ans.is_integer():
            raise ArithmeticError(f"'{num1} {sym} {num2}': {num1} is not divisible by {num2}")
        return int(ans)
    else:
        return int(str(num1) + str(num2))


def brute_force(target: int, nums: List[int], syms: List[Literal["+", "-", "*", "/", "&"]]) \
        -> Generator[List[Tuple[int, Literal["+", "-", "*", "/", "&"], int]], None, None]:
    if not all(map(lambda x: isinstance(x, int), nums)):
        raise ValueError("'nums' should only be comprised of integers")
    if not all(map(lambda x: x in VALID_OPERATIONS, syms)):
        raise ValueError(f"values of 'syms' should be one of the following: {VALID_OPERATIONS}")
    if not isinstance(target, int):
        raise TypeError(f"'target' should be '{int.__name__}', not {type(target).__name__}")

    def _inner(_nums, _syms, history=None):
        if history is None:
            history = []
        if len(_nums) == 1 and len(_syms) == 0 and _nums[0] == target:
            yield history
            return

        _syms.extend(["&"] * (len(_nums) - len(_syms) - 1))
        for sym in VALID_OPERATIONS:
            if sym not in _syms:
                continue

            _syms_copied = copy(_syms)
            _syms_copied.remove(sym)
            for idx, num1 in enumerate(_nums[:-1]):
                for num2 in _nums[idx + 1:]:
                    for _ in range(2):
                        try:
                            result = calc(num1, sym, num2)
                        except ArithmeticError:
                            pass
                        else:
                            numbers_copied = copy(_nums)
                            numbers_copied.remove(num1)
                            numbers_copied.remove(num2)
                            numbers_copied.append(result)

                            history_copied = copy(history)
                            history_copied.append(f"{num1} {sym} {num2}")

                            yield from _inner(numbers_copied, _syms_copied, history_copied)

                        if sym in ("-", "/", "&") and num1 != num2:
                            num1, num2 = num2, num1
                        else:
                            break

    return _inner(nums, syms)


def fetch_data(authorization: str) -> dict:
    headers = {
        "authorization": authorization
    }
    search_result = search(r'(?<="userId":")\d*', str(b64decode(authorization.removeprefix("Bearer ") + "==")))
    if search_result is None:
        raise ValueError("invalid token")
    params = {
        "uid": search_result[0],
        "time": time() * 1000
    }
    return post(URL, headers=headers, params=params).json()["data"]


def resolve_map(game_map: List[List[Union[int, float]]]) -> Tuple[List[int], List[Literal["+", "-", "*", "/"]]]:
    nums = []
    syms = []
    for item in chain(*game_map):
        if isinstance(item, int):
            nums.append(item)
        elif item == 0.3:
            syms.append("+")
        elif item == 0.4:
            syms.append("-")
        elif item == 0.5:
            syms.append("*")
        elif item == 0.6:
            syms.append("/")
    return nums, syms


if __name__ == "__main__":
    # Edit here
    MY_TOKEN = "Bearer xxx"

    last_level = None
    while True:
        data = fetch_data(MY_TOKEN)
        level = data["round"]
        if last_level != level:
            print("Level", level)
            print()
            steps = next(brute_force(data["target"], *resolve_map(data["map"])))
            for step in steps:
                print(step)
            print()
            last_level = level
        sleep(3)
