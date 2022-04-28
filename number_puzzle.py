from collections import defaultdict
from collections.abc import Iterable
from copy import deepcopy
from enum import Enum
from itertools import zip_longest
from operator import add, sub
from typing import List, Tuple, Literal, Any
from uuid import uuid4


class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"
    UP = "U"
    DOWN = "D"


class NumberPuzzle:
    def __init__(self, puzzle: List[List[int | float]], target: int):
        # Parameter validation
        if not self.is_number(target):
            raise ValueError(f"target should be a non-negative integer, not {target}")
        if not isinstance(puzzle, list):
            raise TypeError("malformed puzzle")

        self.pieces = defaultdict(set)
        self.obstacles = set()
        self.__zobrist_keys = {}
        self.__zobrist_hash = 0
        has_piece = False
        first_row_width = None
        for y, row in enumerate(puzzle):
            if not isinstance(row, Iterable):
                raise TypeError("malformed puzzle")

            for x, item in enumerate(row):
                if self.is_piece(item):
                    has_piece = True
                    self.pieces[item].add((x, y))
                    self.__calc_hash(x, y, item)
                elif self.is_obstacle(item):
                    self.obstacles.add((x, y))
                    self.__calc_hash(x, y, item)
                elif not self.is_blank(item):
                    raise ValueError(f"invalid value '{item}' in puzzle")

            if first_row_width is None:
                first_row_width = len(row)
            elif len(row) != first_row_width:
                raise TypeError("malformed puzzle")

        if not has_piece:
            raise ValueError("no pieces in the puzzle")

        # Initialization
        self.LENGTH = len(puzzle[0])
        self.WIDTH = len(puzzle)
        self.puzzle = deepcopy(puzzle)
        self.target = target
        self.history = []  # Only storing `move` method calls (with their arguments) history
        self.__full_history = []  # For inner use, storing every action (move/concat/eval) performed

    def __getitem__(self, item):
        if isinstance(item, tuple):
            if item[0] < 0 or item[1] < 0:
                raise IndexError(f"coordinates should ne non-negative, not ({item[0]}, {item[1]})")
            # self.puzzle[y][x] is the same as self[x, y]
            return self.puzzle[item[1]][item[0]]
        return self.puzzle[item]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            if key[0] < 0 or key[1] < 0:
                raise IndexError(f"coordinates should ne non-negative, not ({key[0]}, {key[1]})")
            # self.puzzle[y][x] is the same as self[x, y]
            self.puzzle[key[1]][key[0]] = value
        else:
            self.puzzle[key] = value

    @property
    def zobrist_hash(self) -> int:
        return self.__zobrist_hash

    # noinspection PyTypeHints
    @staticmethod
    def calc(num1: int, symbol: Literal[0.3, 0.4, 0.5, 0.6, 0.7], num2: int) -> int:
        if not (NumberPuzzle.is_number(num1) and NumberPuzzle.is_number(num2)):
            raise ValueError(f"could not perform operation on: {num1} and {num2}")
        match symbol:
            case 0.3:  # +
                return num1 + num2
            case 0.4:  # -
                if num1 < num2:
                    raise ArithmeticError(f"could not subtract {num2} from {num1}")
                return num1 - num2
            case 0.5:  # *
                return num1 * num2
            case 0.6:  # /
                if not (ans := num1 / num2).is_integer():
                    raise ArithmeticError(f"{num1} is not divisible by {num2}")
                return int(ans)
            # Self-defined operator 0.7 ('&') -> 3 & 7 = 37, 7 & 3 = 73
            case 0.7:
                return int(str(num1) + str(num2))
            case _:
                raise ValueError(f"unrecognized operator: {symbol}")

    @staticmethod
    def is_number(value: Any) -> bool:  # Numbers in the puzzle, non-negative
        return isinstance(value, int) and value >= 0

    @staticmethod
    def is_symbol(value: Any) -> bool:  # Inherit the representation of +, -, *, / in Juejin API
        return value in (0.3, 0.4, 0.5, 0.6)

    @staticmethod
    def is_piece(value: Any) -> bool:  # Movable pieces in the puzzle
        return NumberPuzzle.is_number(value) or NumberPuzzle.is_symbol(value)

    @staticmethod
    def is_blank(value: Any) -> bool:
        return value == 0.1

    @staticmethod
    def is_obstacle(value: Any) -> bool:
        return value == 0.2

    @staticmethod
    def is_valid_value(value: Any) -> bool:  # Check if it is a valid value on the game board
        return NumberPuzzle.is_piece(value) or NumberPuzzle.is_obstacle(value) or NumberPuzzle.is_blank(value)

    def __calc_hash(self, x, y, piece) -> None:
        if self.__zobrist_keys.get((x, y, piece)) is None:
            self.__zobrist_keys[x, y, piece] = int(uuid4())
        self.__zobrist_hash ^= self.__zobrist_keys[x, y, piece]

    def __move_piece(self, from_x: int, from_y: int, to_x: int, to_y: int) -> None:
        # Move a piece all the way horizontally or vertically until it meets another piece or an obstacle
        # Therefore, either from_x == to_x or from_y == to_y in order to be valid
        # Still no parameter validation here, as we are simply 'teleporting' a piece from one place to another
        # `__move` method will find a legal (to_x, to_y) for this
        value = self[from_x, from_y]
        self[from_x, from_y], self[to_x, to_y] = 0.1, value

        self.pieces[value].remove((from_x, from_y))
        self.__calc_hash(from_x, from_y, value)
        self.pieces[value].add((to_x, to_y))
        self.__calc_hash(from_x, from_y, value)
        self.__full_history.append(("move", from_x, from_y, to_x, to_y))

    # noinspection PyTypeHints
    # Concatenate two numbers, just like strings
    def __concat_numbers(self, from_x: int, to_x: int, y: int) -> Tuple[Tuple[int, int], Tuple[int, Literal[0.7], int]]:
        num1, num2 = self[from_x, y], self[to_x, y]
        # Result is evaluating from left to right, swap the numbers if to_x < from_x
        ans = self.calc(num2, 0.7, num1) if from_x > to_x else self.calc(num1, 0.7, num2)
        self[from_x, y], self[to_x, y] = 0.1, ans

        self.pieces[num1].remove((from_x, y))
        self.__calc_hash(from_x, y, num1)
        self.pieces[num2].remove((to_x, y))
        self.__calc_hash(to_x, y, num2)
        self.pieces[ans].add((to_x, y))
        self.__calc_hash(to_x, y, ans)
        self.__full_history.append(("concat", num1, num2, from_x, to_x, y))
        return (to_x, y), (num2, 0.7, num1) if from_x > to_x else (num1, 0.7, num2)

    # noinspection PyTypeHints
    def __eval_numbers(self, symbol_x: int, y: int) \
            -> Tuple[Tuple[int, int], Tuple[int, Literal[0.3, 0.4, 0.5, 0.6], int]]:
        # Make sure that the expression is evaluated from left to right
        if (val1_x := symbol_x - 1) > (val2_x := symbol_x + 1):
            val1_x, val2_x = val2_x, val1_x

        val1, symbol, val2 = self[val1_x, y], self[symbol_x, y], self[val2_x, y]

        ans = self.calc(val1, symbol, val2)  # Might raise ArithmeticError
        self[val1_x, y], self[symbol_x, y], self[val2_x, y] = 0.1, ans, 0.1

        self.pieces[val1].remove((val1_x, y))
        self.__calc_hash(val1_x, y, val1)
        self.pieces[symbol].remove((symbol_x, y))
        self.__calc_hash(symbol_x, y, symbol)
        self.pieces[val2].remove((val2_x, y))
        self.__calc_hash(val2_x, y, val2)
        self.pieces[ans].add((symbol_x, y))
        self.__calc_hash(symbol_x, y, ans)
        self.__full_history.append(("eval", val1, symbol, val2, symbol_x, y))
        return (symbol_x, y), (val1, symbol, val2)

    def __find_destination_and_move(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
        is_increasing = direction in (Direction.RIGHT, Direction.DOWN)
        is_moving_horizontally = direction in (Direction.LEFT, Direction.RIGHT)
        if is_increasing:
            start = x + 1 if is_moving_horizontally else y + 1
            stop = self.LENGTH if is_moving_horizontally else self.WIDTH
            step = 1
        else:
            start = x - 1 if is_moving_horizontally else y - 1
            stop = -1
            step = -1

        changed = False
        for loc in range(start, stop, step):
            val_at_loc = self[loc, y] if is_moving_horizontally else self[x, loc]
            if not self.is_blank(val_at_loc):
                loc -= step
                break
            changed = True

        if not changed:
            return x, y
        if is_moving_horizontally:
            self.__move_piece(x, y, loc, y)
            return loc, y
        else:
            self.__move_piece(x, y, x, loc)
            return x, loc

    # noinspection PyTypeHints
    def move(self, x: int, y: int, direction: Direction) \
            -> Tuple[Tuple[int, int], Tuple[int, Literal[0.3, 0.4, 0.5, 0.6, 0.7], int] | None]:
        """Move a piece. A move that does not make a change to the puzzle will not be recorded.

        :param x: x-coordinate of the piece
        :type x: int
        :param y: y-coordinate of the piece
        :type y: int
        :param direction: moving direction, either left, right, up or down
        :type direction: Direction
        :return: final (x, y) coordinate of the piece after moving
        :rtype: Tuple[int, int]
        :raises ValueError: index out of range or invalid `direction`
        :raises TypeError: no pieces on the coordinate given
        """
        if not self.is_piece(self[x, y]):
            raise TypeError(f"no movable pieces on ({x}, {y})")
        if not isinstance(direction, Direction):
            raise ValueError("invalid direction")

        original_x, original_y = x, y
        # A move may yield:
        #   - move
        #   - move + eval
        #   - move + concat
        #   - eval
        #   - concat
        # We need something to separate moves: None (as a header of each move)
        self.__full_history.append(None)
        operands = None
        x, y = self.__find_destination_and_move(x, y, direction)

        if direction in (Direction.LEFT, Direction.RIGHT):
            plus_minus = add if direction == Direction.RIGHT else sub

            if self.is_number(self[x, y]) and 0 <= (next_or_last_x := plus_minus(x, 1)) < self.WIDTH:
                if self.is_number(self[next_or_last_x, y]):
                    (x, y), operands = self.__concat_numbers(x, next_or_last_x, y)  # from_x, to_x, y
                elif 0 <= (next_next_or_last_last_x := plus_minus(next_or_last_x, 1)) < self.WIDTH and \
                        self.is_symbol(self[next_or_last_x, y]) and \
                        self.is_number(self[next_next_or_last_last_x, y]):
                    try:
                        (x, y), operands = self.__eval_numbers(next_or_last_x, y)  # symbol_x, y
                    except ArithmeticError:
                        pass

        # If no changes, pop `None`
        if original_x == x and original_y == y:
            self.__full_history.pop()
        else:
            self.history.append((original_x, original_y, direction))
        return (x, y), operands

    def is_solved(self) -> bool:
        """Check whether the puzzle is solved.

        :return: state of the puzzle
        :rtype: bool
        """
        raise NotImplementedError  # todo

    def reset(self) -> None:
        """Reset the puzzle to the initial, same as calling `undo` method infinite times.

        :return: None
        """
        self.undo(len(self.__full_history))

    def restore_state_to(self, history: List[Tuple[int, int, Direction]]) -> None:
        longest_common_prefix_length = 0
        for longest_common_prefix_length, (this, that) in enumerate(zip_longest(self.history, history)):
            if this != that:
                break

        self.undo(len(self.history) - longest_common_prefix_length)
        for args in history[longest_common_prefix_length:]:
            self.move(*args)

    def undo(self, move_count: int = 1) -> None:
        """Return the state of the puzzle to `move_count` number of moves before.

        :param move_count: the number of steps to undo, default to 1
        :type move_count: int
        :return: None
        :raises ValueError: invalid `move_count`
        """
        for _ in range(move_count):  # Undo `move_count` times
            if len(self.__full_history) == 0:  # `move_count` > len(history)
                break

            while True:
                item = self.__full_history.pop()
                if item is None:
                    break

                cmd, *args = item
                match cmd:
                    case "move":
                        from_x, from_y, to_x, to_y = args
                        val = self[to_x, to_y]
                        self[from_x, from_y], self[to_x, to_y] = val, 0.1

                        self.pieces[val].add((from_x, from_y))
                        self.__calc_hash(from_x, from_y, val)
                        self.pieces[val].remove((to_x, to_y))
                        self.__calc_hash(to_x, to_y, val)
                    case "concat":
                        val1, val2, from_x, to_x, y = args
                        val_after = self[to_x, y]
                        self[from_x, y], self[to_x, y] = val1, val2

                        self.pieces[val_after].remove((to_x, y))
                        self.__calc_hash(to_x, y, val_after)
                        self.pieces[val1].add((from_x, y))
                        self.__calc_hash(from_x, y, val1)
                        self.pieces[val2].add((to_x, y))
                        self.__calc_hash(to_x, y, val2)
                    case "eval":
                        val1, symbol, val2, symbol_x, y = args
                        val1_x = symbol_x - 1
                        val2_x = symbol_x + 1
                        val_after = self[symbol_x, y]
                        self[val1_x, y], self[symbol_x, y], self[val2_x, y] = val1, symbol, val2

                        self.pieces[val_after].remove((symbol_x, y))
                        self.__calc_hash(symbol_x, y, val_after)
                        self.pieces[val1].add((val1_x, y))
                        self.__calc_hash(val1_x, y, val1)
                        self.pieces[symbol].add((symbol_x, y))
                        self.__calc_hash(symbol_x, y, symbol)
                        self.pieces[val2].add((val2_x, y))
                        self.__calc_hash(val2_x, y, val2)
            self.history.pop()
