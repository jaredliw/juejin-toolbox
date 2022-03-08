from collections import defaultdict
from collections.abc import Iterable
from copy import deepcopy
from enum import Enum
from itertools import zip_longest
from operator import add, sub
from typing import List, Tuple, Literal, Any


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
        has_piece = False
        first_row_width = None
        for y, row in enumerate(puzzle):
            if not isinstance(row, Iterable):
                raise TypeError("malformed puzzle")

            for x, item in enumerate(row):
                if self.is_piece(item):
                    has_piece = True
                    self.pieces[item].add((x, y))
                elif self.is_obstacle(item):
                    self.obstacles.add((x, y))
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
            return self.puzzle[item[1]][item[0]]  # Alias self.puzzle[y][x] -> self[x, y]
        return self.puzzle[item]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            self.puzzle[key[1]][key[0]] = value  # Alias self.puzzle[y][x] -> self[x, y]
        else:
            self.puzzle[key] = value

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
            case 0.7:  # Self-defined operator 0.7 ('&') -> 3 & 7 = 37, 7 & 3 = 73
                return int(str(num1) + str(num2))
            case _:
                raise ValueError(f"unrecognized operator: {symbol}")

    @staticmethod
    def is_number(value: Any) -> bool:  # Refer to numbers in the puzzle, non-negative
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
    def is_valid_value(value: Any) -> bool:  # Check if it is a valid value in the puzzle
        return NumberPuzzle.is_piece(value) or NumberPuzzle.is_obstacle(value) or NumberPuzzle.is_blank(value)

    def __move_piece(self, from_x: int, from_y: int, to_x: int, to_y: int) -> None:
        # Move a piece all the way horizontally or vertically until it meets another piece or an obstacle
        # Therefore, either from_x == to_x or from_y == to_y in order to be valid
        # Still no parameter validation here, as we are simply 'teleporting' a piece from one place to another
        # `__move` method will find a legal (to_x, to_y) for this
        value = self[from_x, from_y]
        self[from_x, from_y], self[to_x, to_y] = 0.1, value

        self.pieces[value].remove((from_x, from_y))
        self.pieces[value].add((to_x, to_y))
        self.__full_history.append(("move", from_x, from_y, to_x, to_y))

    def __concat_numbers(self, from_x: int, to_x: int, y: int) -> Tuple[Tuple[int, int], Tuple[int, Literal[0.7], int]]:
        # Concatenate two numbers, just like strings
        if to_x < 0 or to_x >= self.LENGTH or \
                not self.is_number(self[from_x, y]) or \
                not self.is_number(self[to_x, y]):
            raise ValueError("invalid operation")

        val1, val2 = self[from_x, y], self[to_x, y]
        # Custom '&' operator does not obey the commutative law, i.e. 7 & 3 != 3 & 7
        # Result is evaluating from left to right
        # E.g. 7, 3, swiping to the right -> 0.1, 73
        #      7, 3, swiping to the left  -> 73, 0.1
        # Only swap the values, but not the indices; as the result has to be at (to_x, y)
        ans = self.calc(val2, 0.7, val1) if from_x > to_x else self.calc(val1, 0.7, val2)
        self[from_x, y], self[to_x, y] = 0.1, ans

        self.pieces[val1].remove((from_x, y))
        self.pieces[val2].remove((to_x, y))
        self.pieces[ans].add((to_x, y))
        self.__full_history.append(("concat", val1, val2, from_x, to_x, y))
        return (to_x, y), (val2, 0.7, val1) if from_x > to_x else (val1, 0.7, val2)

    def __eval_numbers(self, symbol_x: int, y: int) \
            -> Tuple[Tuple[int, int], Tuple[int, Literal[0.3, 0.4, 0.5, 0.6], int]]:
        val1_x = symbol_x - 1
        val2_x = symbol_x + 1
        if val1_x < 0 or val1_x >= self.LENGTH or val2_x < 0 or val2_x >= self.LENGTH or \
                not self.is_number(self[y][val1_x]) or \
                not self.is_symbol(self[symbol_x, y]) or \
                not self.is_number(self[y][val2_x]):
            raise ValueError("invalid operation")

        # Make sure that the expression is evaluated from left to right
        if val1_x > val2_x:
            val1_x, val2_x = val2_x, val1_x
        val1, symbol, val2 = self[y][val1_x], self[symbol_x, y], self[y][val2_x]

        try:
            ans = self.calc(val1, symbol, val2)
        except ArithmeticError:
            raise ValueError("invalid operation")
        self[y][val1_x], self[symbol_x, y], self[y][val2_x] = 0.1, ans, 0.1

        self.pieces[val1].remove((val1_x, y))
        self.pieces[symbol].remove((symbol_x, y))
        self.pieces[val2].remove((val2_x, y))
        self.pieces[ans].add((symbol_x, y))
        self.__full_history.append(("eval", val1, symbol, val2, val1_x, val2_x, y))
        return (symbol_x, y), (val1, symbol, val2)

    def __move(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
        is_increasing = direction in (Direction.RIGHT, Direction.DOWN)
        is_moving_horizontally = direction in (Direction.LEFT, Direction.RIGHT)
        if is_increasing:
            bound = self.LENGTH if is_moving_horizontally else self.WIDTH
        else:
            bound = -1
        step = 1 if is_increasing else -1
        plus_minus = add if is_increasing else sub

        # todo: optimize
        dest = x if is_moving_horizontally else y
        dest_changed = False
        for loc in range(plus_minus(dest, 1), bound, step):
            val_at_loc = self[loc, y] if is_moving_horizontally else self[x, loc]
            if self.is_blank(val_at_loc):
                dest = loc
                dest_changed = True
            else:
                break

        if not dest_changed:
            raise ValueError("Invalid operation")
        if is_moving_horizontally:
            self.__move_piece(x, y, dest, y)
            return dest, y
        else:
            self.__move_piece(x, y, x, dest)
            return x, dest

    def move(self, x: int, y: int, direction: Direction) \
            -> Tuple[Tuple[int, int], Tuple[int, Literal[0.3, 0.4, 0.5, 0.6, 0.7], int] | None]:
        """Move a piece. A move that does not make a change to the puzzle will be omitted.

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
        # Parameter validation
        if x < 0 or y < 0:
            raise ValueError(f"coordinates should be non-negative, not ({x}, {y})")
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
        # We need something to separate them: None (as a header of each move)
        self.__full_history.append(None)
        operands = None
        try:
            x, y = self.__move(x, y, direction)
        except ValueError:
            pass

        if direction in (Direction.LEFT, Direction.RIGHT):
            plus_minus = add if direction == Direction.RIGHT else sub
            try:
                (x, y), operands = self.__concat_numbers(x, plus_minus(x, 1), y)
            except ValueError:
                pass
            try:
                (x, y), operands = self.__eval_numbers(plus_minus(x, 1), y)
            except ValueError:
                pass

        if original_x == x and original_y == y:  # if no change
            self.__full_history.pop()  # Pop `None`
        else:
            self.history.append((original_x, original_y, direction))
        return (x, y), operands

    def is_solved(self) -> bool:
        """Check whether the puzzle is solved.

        :return: state of the puzzle
        :rtype: bool
        """
        raise NotImplementedError
        # todo
        # if len(self.pieces) != 1:
        #     return False
        # x, y = self.pieces.pop()
        # self.
        # return self[x, y] == self.target

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
                        self.pieces[val].remove((to_x, to_y))
                    case "concat":
                        val1, val2, from_x, to_x, y = args
                        val_after = self[to_x, y]
                        self[from_x, y], self[to_x, y] = val1, val2

                        self.pieces[val_after].remove((to_x, y))
                        self.pieces[val1].add((from_x, y))
                        self.pieces[val2].add((to_x, y))
                    case "eval":
                        val1, symbol, val2, leftmost_x, rightmost_x, y = args
                        val_after = self[y][leftmost_x + 1]
                        self[leftmost_x, y], self[y][leftmost_x + 1], self[rightmost_x, y] \
                            = val1, symbol, val2

                        self.pieces[val_after].remove((leftmost_x + 1, y))
                        self.pieces[val1].add((leftmost_x, y))
                        self.pieces[symbol].add((leftmost_x + 1, y))
                        self.pieces[val2].add((rightmost_x, y))
            self.history.pop()
