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
        if not len(game_map) == self.__MAP_WIDTH or not all(map(lambda arr: len(arr) == self.__MAP_LENGTH, game_map)):
            raise ValueError(f"malformed game map, should be a {self.__MAP_LENGTH} by {self.__MAP_WIDTH} grid")
        if not self.__is_number(target):
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
        self.__move_history = []
        self.__actions = []

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
            case 0.7:
                return int(str(num1) + str(num2))
            case _:
                raise ValueError(f"unknown symbol: {symbol}")

    @staticmethod
    def __is_number(value: Any) -> bool:  # Refer to numbers in the game, non-negative
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
    def __is_valid(value: Any) -> bool:
        return Game.__is_element(value) or Game.__is_obstacle(value) or Game.__is_blank(value)

    def __move_number(self, from_x: int, from_y: int, to_x: int, to_y: int) -> None:
        self.game_map[from_y][from_x], self.game_map[to_y][to_x] = 0.1, self.game_map[from_y][from_x]
        self.__elements.remove((from_x, from_y))
        self.__elements.add((to_x, to_y))
        self.__actions.append(("move", from_x, from_y, to_x, to_y))

    def __join_numbers(self, from_x: int, to_x: int, y: int) -> Tuple[int, int]:  # todo incorrect when undo()
        val1, val2 = self.game_map[y][from_x], self.game_map[y][to_x]
        if val1 > val2:
            val1, val2 = val2, val1
        self.game_map[y][from_x], self.game_map[y][to_x] = 0.1, self.__calc(val1, 0.7, val2)

        self.__elements.remove((from_x, y))
        self.__elements.add((to_x, y))
        self.__actions.append(("join", val1, val2, from_x, to_x, y))
        return to_x, y

    def __eval_numbers(self, val1_x: int, symbol_x: int, val2_x: int, y: int) -> Tuple[int, int]:
        if val1_x > val2_x:
            val1_x, val2_x = val2_x, val1_x
        val1, symbol, val2 = self.game_map[y][val1_x], self.game_map[y][symbol_x], self.game_map[y][val2_x]

        self.game_map[y][val1_x], self.game_map[y][symbol_x], self.game_map[y][val2_x] \
            = 0.1, self.__calc(val1, symbol, val2), 0.1

        self.__elements.remove((val1_x, y))
        self.__elements.remove((val2_x, y))
        self.__actions.append(("eval", val1, symbol, val2, val1_x, val2_x, y))
        return symbol_x, y

    def __move(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
        is_increasing = direction in (Direction.RIGHT, Direction.DOWN)
        is_moving_horizontally = direction in (Direction.LEFT, Direction.RIGHT)
        if is_increasing:
            bound = self.__MAP_LENGTH if is_moving_horizontally else self.__MAP_WIDTH
        else:
            bound = -1
        step = 1 if is_increasing else -1
        plus_minus = add if is_increasing else sub

        dest = x if is_moving_horizontally else y
        dest_changed = False
        for loc in range(plus_minus(dest, 1), bound, step):
            val_at_dest = self.game_map[y][loc] if is_moving_horizontally else self.game_map[loc][x]
            if self.__is_blank(val_at_dest):
                dest = loc
                dest_changed = True
            else:
                break

        if not dest_changed:
            return x, y
        if is_moving_horizontally:
            self.__move_number(x, y, dest, y)
            return dest, y
        else:
            self.__move_number(x, y, x, dest)
            return x, dest

    def move(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
        if not self.__is_number(x) or x >= self.__MAP_LENGTH:
            raise ValueError("invalid 'x'")
        if not self.__is_number(y) or y >= self.__MAP_WIDTH:
            raise ValueError("invalid 'y'")
        if not self.__is_element(self.game_map[y][x]):
            raise ValueError(f"no element on location: ({x}, {y})")
        if not isinstance(direction, Direction):
            raise ValueError("invalid 'direction'")

        self.__actions.append(None)  # Custom separator
        new_x, new_y = self.__move(x, y, direction)

        if direction in (Direction.LEFT, Direction.RIGHT):
            plus_minus = add if direction == Direction.RIGHT else sub
            if (join_res := self.__join_numbers_handler(x, plus_minus(x, 1), y)) is not None:
                self.__move_history.append((x, y, direction))
                return join_res
            elif (val_res := self.__eval_numbers_handler(x, plus_minus(x, 1), plus_minus(x, 2), y)) is not None:
                self.__move_history.append((x, y, direction))
                return val_res

        if (x, y) != (new_x, new_y):
            self.__move_history.append((x, y, direction))
        else:
            self.__actions.pop()  # Pop none
        return new_x, new_y

    def __join_numbers_handler(self, from_x: int, to_x: int, y: int) -> Union[None, Tuple[int, int]]:
        # from_x won't be < 0
        if to_x < 0 or to_x >= self.__MAP_LENGTH or not self.__is_number(self.game_map[y][to_x]):
            return None

        return self.__join_numbers(from_x, to_x, y)

    def __eval_numbers_handler(self, val1_x: int, symbol_x: int, val2_x: int, y: int) -> Union[None, Tuple[int, int]]:
        if val1_x < 0 or val1_x >= self.__MAP_LENGTH or val2_x < 0 or val2_x >= self.__MAP_LENGTH or \
                not self.__is_symbol(self.game_map[y][symbol_x]) or \
                not self.__is_number(self.game_map[y][val2_x]):
            return None

        return self.__eval_numbers(val1_x, symbol_x, val2_x, y)

    def get_elements(self) -> Set[Tuple[int, int]]:
        return deepcopy(self.__elements)

    def is_success(self) -> bool:
        if len(elements := self.get_elements()) != 1:
            return False
        x, y = elements.pop()
        return self.game_map[y][x] == self.target

    def get_history(self) -> List[Tuple[int, int, Direction]]:
        return self.__move_history

    def reset(self) -> None:
        self.undo(len(self.__actions))

    def undo(self, move_count: int = 1) -> None:
        if not isinstance(move_count, int) or move_count < 0:
            raise ValueError("invalid 'n': not a positive integer")

        for _ in range(move_count):
            if len(self.__actions) == 0:
                break

            while True:
                item = self.__actions.pop()
                if item is None:
                    break

                cmd, *args = item
                match cmd:
                    case "move":
                        from_x, from_y, to_x, to_y = args
                        self.game_map[from_y][from_x], self.game_map[to_y][to_x] = self.game_map[to_y][to_x], 0.1

                        move_count -= 1
                        self.__move_history.pop()
                    case "join":
                        val1, val2, from_x, to_x, y = args
                        self.game_map[y][from_x], self.game_map[y][to_x] = val1, val2
                    case "eval":
                        val1, symbol, val2, leftmost_x, rightmost_x, y = args
                        self.game_map[y][leftmost_x], self.game_map[y][leftmost_x + 1], self.game_map[y][rightmost_x] \
                            = val1, symbol, val2
                    case _:
                        raise ValueError(f"unknown command: '{cmd}'")
            self.__move_history.pop()
