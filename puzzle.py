from base64 import b64decode
from itertools import chain, zip_longest
from random import shuffle
from time import time, sleep
from typing import List, Literal, Tuple, Union

from regex import search
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


def brute_force(target: int, nums: List[int], syms: List[Literal["+", "-", "*", "/", "&"]], timeout: int = 60) -> list:
    if not all(map(lambda x: isinstance(x, int), nums)):
        raise ValueError("'nums' should only be comprised of integers")
    if not all(map(lambda x: x in VALID_OPERATIONS, syms)):
        raise ValueError(f"values of 'syms' should be one of the following: {VALID_OPERATIONS}")
    if not isinstance(target, int):
        raise TypeError(f"'target' should be '{int.__name__}', not {type(target).__name__}")

    try:
        start_time = time()
        for _ in range(len(nums) - len(syms) - 1):
            syms.append("&")

        while True:
            if time() - start_time > timeout:
                raise TimeoutError("time limit exceeds")
            shuffle(nums)
            shuffle(syms)
            exp = list(chain(*zip_longest(nums, syms)))[:-1]

            precedence = list(range(1, len(syms) + 1))
            shuffle(precedence)

            steps = []
            flag = False
            for n in range(1, len(syms) + 1):
                loc = precedence.index(n)
                precedence.pop(loc)

                loc *= 2
                try:
                    operands = [exp.pop(loc), exp.pop(loc), exp.pop(loc)]
                    exp.insert(loc, calc(*operands))
                    steps.append(" ".join(map(str, operands)))
                except ArithmeticError:
                    flag = True
                    break
            if flag:
                continue

            if exp[0] == target:
                return steps
    except (TimeoutError, KeyboardInterrupt) as e:
        raise e
    except:
        raise ValueError("puzzle not solvable") from None


def fetch_data(authorization: str) -> dict:
    headers = {
        "authorization": authorization
    }
    params = {
        "uid": search(r'(?<="userId":")\d*', str(b64decode(authorization.removeprefix("Bearer "))))[0],
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
            for step in brute_force(data["target"], *resolve_map(data["map"])):
                print(step)
            print()
            last_level = level
        sleep(3)
