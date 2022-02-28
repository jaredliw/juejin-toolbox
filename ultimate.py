from copy import deepcopy
from enum import Enum
from operator import add, sub
from typing import List, Union, Tuple, Literal, Any, Set


class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"
    UP = "U"
    DOWN = "D"


class Game:
    __MAP_LENGTH = 7
    __MAP_WIDTH = 7

    def __init__(self, game_map: List[List[Union[float, int]]], target: int):
        if not len(game_map) == self.__MAP_LENGTH or not all(map(lambda arr: len(arr) == self.__MAP_WIDTH, game_map)):
            raise ValueError(f"malformed game map, should be a {self.__MAP_LENGTH} by {self.__MAP_WIDTH} grid")
        if not isinstance(target, int) or target < 0:
            raise ValueError("invalid 'target'")

        self.__elements = set()
        for y, row in enumerate(game_map):
            for x, item in enumerate(row):
                if not self.__is_valid(item):
                    raise ValueError(f"invalid value '{item}' in 'game_map'")

                if self.__is_element(item):
                    self.__elements.add((x, y))

        self.game_map = deepcopy(game_map)
        self.target = target
        self.__history = []

    @staticmethod
    def __calc(num1: int, symbol: Literal[0.3, 0.4, 0.5, 0.6, 0.7], num2: int) -> int:
        match symbol:
            case 0.3:
                return num1 + num2
            case 0.4:
                if num1 < num2:
                    raise ArithmeticError(f"could not subtract {num2} from {num1}")
                return num1 - num2
            case 0.5:
                return num1 * num2
            case 0.6:
                if not (ans := num1 / num2).is_integer():
                    raise ArithmeticError(f"{num1} is not divisible by {num2}")
                return int(ans)
            case _:
                return int(str(num1) + str(num2))

    @staticmethod
    def __is_number(value: Any) -> bool:
        return isinstance(value, int) and value >= 0

    @staticmethod
    def __is_symbol(value: Any) -> bool:
        return value in (0.3, 0.4, 0.5, 0.6)

    @staticmethod
    def __is_element(value: Any) -> bool:
        return Game.__is_number(value) or Game.__is_symbol(value)

    @staticmethod
    def __is_blank(value: Any) -> bool:
        return value == 0.1

    @staticmethod
    def __is_obstacle(value: Any) -> bool:
        return value == 0.2

    @staticmethod
    def __is_value(value: Any) -> bool:
        return Game.__is_element(value) or Game.__is_blank(value) or Game.__is_obstacle(value)

    @staticmethod
    def __is_valid(value: Any) -> bool:
        return Game.__is_element(value) or Game.__is_obstacle(value) or Game.__is_blank(value)

    def __move_number(self, from_x: int, from_y: int, to_x: int, to_y: int) -> None:
        self.game_map[from_y][from_x], self.game_map[to_y][to_x] = 0.1, self.game_map[from_y][from_x]
        self.__elements.remove((from_x, from_y))
        self.__elements.add((to_x, to_y))

    def __join_numbers(self, from_x: int, to_x: int, y: int) -> Union[Tuple[int, int], None]:
        try:
            if abs(from_x - to_x) != 1 or from_x < 0 or to_x < 0 or y < 0 or \
                    not self.__is_number(val1 := self.game_map[y][from_x]) or \
                    not self.__is_number(val2 := self.game_map[y][to_x]):
                return None

            self.game_map[y][from_x], self.game_map[y][to_x] = 0.1, self.__calc(val1, "&", val2)
        except IndexError:
            return None

        self.__elements.remove((from_x, y))
        self.__elements.add((to_x, y))
        return to_x, y

    def __eval_numbers(self, val1_x: int, symbol_x: int, val2_x: int, y: int) -> Union[Tuple[int, int], None]:
        try:
            if abs(val1_x - symbol_x) != 1 or abs(val2_x - symbol_x) != 1 or \
                    val1_x < 0 or val2_x < 0 or symbol_x < 0 or y < 0 or \
                    not self.__is_number(val1 := self.game_map[y][val1_x]) or \
                    not self.__is_symbol(symbol := self.game_map[y][symbol_x]) or \
                    not self.__is_number(val2 := self.game_map[y][val2_x]):
                return None

            if val1_x > val2_x:
                val1_x, val2_x = val2_x, val1_x
                val1, val2 = val2, val1

            self.game_map[y][val1_x], self.game_map[y][symbol_x], self.game_map[y][val2_x] \
                = 0.1, self.__calc(val1, symbol, val2), 0.1
        except (IndexError, ArithmeticError):
            return None

        self.__elements.remove((val1_x, y))
        self.__elements.remove((val2_x, y))
        return symbol_x, y

    def __move_left_right(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
        original_x = x
        going_right = direction == Direction.RIGHT
        plus_minus = add if going_right else sub
        for new_x in range(x, self.__MAP_LENGTH if going_right else -1, 1 if going_right else -1):
            if self.__is_blank(self.game_map[y][new_x]):
                self.__move_number(x, y, new_x, y)
                x = new_x
            elif (join_res := self.__join_numbers(x, plus_minus(x, 1), y)) is not None:
                return join_res
            elif (val_res := self.__eval_numbers(x, plus_minus(x, 1), plus_minus(x, 2), y)) is not None:
                return val_res
            elif new_x != original_x:
                break
        return x, y

    def __move_up_down(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
        going_down = direction == Direction.DOWN
        plus_minus = add if going_down else sub

        for new_y in range(plus_minus(y, 1), self.__MAP_WIDTH if going_down else -1, 1 if going_down else -1):
            if self.__is_blank(self.game_map[new_y][x]):
                self.__move_number(x, y, x, new_y)
                y = new_y
            else:
                break
        return x, y

    def move(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
        if not self.__is_number(x) or not 0 <= x < self.__MAP_LENGTH:
            raise ValueError("invalid 'x'")
        if not self.__is_number(y) or not 0 <= y < self.__MAP_WIDTH:
            raise ValueError("invalid 'y'")
        if not self.__is_element(self.game_map[y][x]):
            raise ValueError(f"no element on location: ({x}, {y})")
        if not isinstance(direction, Direction):
            raise ValueError("invalid 'direction'")

        self.__history.append((x, y, direction))
        if direction in (Direction.LEFT, Direction.RIGHT):
            return self.__move_left_right(x, y, direction)
        else:
            return self.__move_up_down(x, y, direction)

    def get_elements(self) -> Set[Tuple[int, int]]:
        return deepcopy(self.__elements)

    def is_success(self) -> bool:
        if len(elements := self.get_elements()) != 1:
            return False
        x, y = elements.pop()
        return self.game_map[y][x] == self.target

    def get_history(self) -> List[Tuple[int, int, Direction]]:
        return self.__history

    def undo(self, n: int) -> None:
        if not isinstance(n, int) or n < 0:
            raise ValueError("invalid 'n': not a positive integer")
