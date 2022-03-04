from copy import deepcopy, copy
from enum import Enum
from itertools import zip_longest
from operator import add, sub
from typing import List, Union, Tuple, Literal, Any, Set


class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"
    UP = "U"
    DOWN = "D"


class ShuZiMiTi:
    __PUZZLE_LENGTH = 7
    __PUZZLE_WIDTH = 7

    def __init__(self, puzzle: List[List[Union[float, int]]], target: int):
        # Parameter validation
        if not len(puzzle) == self.__PUZZLE_WIDTH or not all(map(lambda arr: len(arr) == self.__PUZZLE_LENGTH, puzzle)):
            raise ValueError(f"malformed puzzle, should be a {self.__PUZZLE_LENGTH} by {self.__PUZZLE_WIDTH} grid")
        if not self.__is_number(target):
            raise ValueError("invalid 'target'")

        self.__pieces = set()
        for y, row in enumerate(puzzle):
            for x, item in enumerate(row):
                if not self.__is_valid(item):
                    raise ValueError(f"invalid value '{item}' in puzzle")

                if self.__is_piece(item):
                    self.__pieces.add((x, y))

        # Initialization
        self.__puzzle = deepcopy(puzzle)
        self.target = target
        self.__history = []  # Only storing `move` method calls (with their arguments) history
        self.__full_history = []  # For inner use, storing every action (move/concat/eval) performed

    def __getitem__(self, item):
        return self.__puzzle[item]  # Alias self.__puzzle[y][x] -> self[y][x]

    def __setitem__(self, key, value):
        raise AttributeError("puzzle is read-only")  # Inhibit rewriting a row

    @property
    def puzzle(self):
        return deepcopy(self.__puzzle)  # For external use only; use `self.__puzzle` directly in this class

    @puzzle.setter
    def puzzle(self, value):
        raise AttributeError("puzzle is read-only")

    @puzzle.deleter
    def puzzle(self):
        raise AttributeError("puzzle is read-only")

    @staticmethod
    def calc(num1: int, symbol: Literal[0.3, 0.4, 0.5, 0.6, 0.7], num2: int) -> int:
        if not (ShuZiMiTi.__is_number(num1) and ShuZiMiTi.__is_symbol(symbol) and ShuZiMiTi.__is_number(num2)):
            raise ValueError(f"{num1} {symbol} {num2}: invalid operation")
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

    @staticmethod
    def __is_number(value: Any) -> bool:  # Refer to numbers in the puzzle, non-negative
        return isinstance(value, int) and value >= 0

    @staticmethod
    def __is_symbol(value: Any) -> bool:  # Inherit the representation of +, -, *, / in Juejin API
        return value in (0.3, 0.4, 0.5, 0.6)

    @staticmethod
    def __is_piece(value: Any) -> bool:  # Movable pieces in the puzzle
        return ShuZiMiTi.__is_number(value) or ShuZiMiTi.__is_symbol(value)

    @staticmethod
    def __is_blank(value: Any) -> bool:
        return value == 0.1

    @staticmethod
    def __is_obstacle(value: Any) -> bool:
        return value == 0.2

    @staticmethod
    def __is_valid(value: Any) -> bool:  # Check if it is a valid value in the puzzle
        return ShuZiMiTi.__is_piece(value) or ShuZiMiTi.__is_obstacle(value) or ShuZiMiTi.__is_blank(value)

    def __move_element(self, from_x: int, from_y: int, to_x: int, to_y: int) -> None:
        # Move a piece all the way horizontally or vertically until it meets another piece or an obstacle
        # Therefore, either from_x == to_x or from_y == to_y in order to be valid
        # Still no parameter validation here, as we are simply 'teleporting' a piece from one place to another
        # `__move` method will find a legal (to_x, to_y) for this
        self[from_y][from_x], self[to_y][to_x] = 0.1, self[from_y][from_x]

        self.__pieces.remove((from_x, from_y))
        self.__pieces.add((to_x, to_y))
        self.__full_history.append(("move", from_x, from_y, to_x, to_y))

    def __concat_numbers(self, from_x: int, to_x: int, y: int) -> Tuple[int, int]:
        # Concatenate two numbers, just like strings
        # No parameter validation here
        val1, val2 = self[y][from_x], self[y][to_x]
        # Custom '&' operator does not obey the commutative law, i.e. 7 & 3 != 3 & 7
        # In the puzzle, the result is evaluating from left to right
        # E.g. 7, 3, swiping to the right -> 0.1, 73
        #      7, 3, swiping to the left  -> 73, 0.1
        # Note that we only swap the values, but not the indices; as the result has to be at (to_x, y)
        swapped = False
        if from_x > to_x:
            val1, val2 = val2, val1
            swapped = True

        self[y][from_x], self[y][to_x] = 0.1, self.calc(val1, 0.7, val2)

        self.__pieces.remove((from_x, y))
        # Swap again if we swapped them just now
        # This is because val1 is originally at (from_x, y) and val2 is at (to_x, y)
        # If we don't do this, `undo` method (see below) will yield an incorrect result when we undo this step
        if swapped:
            val1, val2 = val2, val1
        self.__full_history.append(("concat", val1, val2, from_x, to_x, y))
        return to_x, y

    def __eval_numbers(self, val1_x: int, symbol_x: int, val2_x: int, y: int) -> Tuple[int, int]:
        # No parameter validation here
        # Unlike the above, the result is always in the middle of three, i.e. (symbol_x, y)

        # Make sure that the expression is evaluated from left to right
        if val1_x > val2_x:
            val1_x, val2_x = val2_x, val1_x
        val1, symbol, val2 = self[y][val1_x], self[y][symbol_x], self[y][val2_x]

        # May cause ArithmeticError
        self[y][val1_x], self[y][symbol_x], self[y][val2_x] \
            = 0.1, self.calc(val1, symbol, val2), 0.1

        self.__pieces.remove((val1_x, y))
        self.__pieces.remove((val2_x, y))
        self.__full_history.append(("eval", val1, symbol, val2, val1_x, val2_x, y))
        return symbol_x, y

    def __move(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
        is_increasing = direction in (Direction.RIGHT, Direction.DOWN)
        is_moving_horizontally = direction in (Direction.LEFT, Direction.RIGHT)
        if is_increasing:
            bound = self.__PUZZLE_LENGTH if is_moving_horizontally else self.__PUZZLE_WIDTH
        else:
            bound = -1
        step = 1 if is_increasing else -1
        plus_minus = add if is_increasing else sub

        # todo: optimize
        dest = x if is_moving_horizontally else y
        dest_changed = False
        for loc in range(plus_minus(dest, 1), bound, step):
            val_at_loc = self[y][loc] if is_moving_horizontally else self[loc][x]
            if self.__is_blank(val_at_loc):
                dest = loc
                dest_changed = True
            else:
                break

        if not dest_changed:
            return x, y
        if is_moving_horizontally:
            self.__move_element(x, y, dest, y)
            return dest, y
        self.__move_element(x, y, x, dest)
        return x, dest

    def move(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
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
        if not self.__is_number(x) or x >= self.__PUZZLE_LENGTH:
            raise IndexError("'x' is out of range")
        if not self.__is_number(y) or y >= self.__PUZZLE_WIDTH:
            raise IndexError("'y' is out of range")
        if not self.__is_piece(self[y][x]):
            raise TypeError(f"no movable pieces on location: ({x}, {y})")
        if not isinstance(direction, Direction):
            raise ValueError("invalid 'direction'")

        # A move may yield:
        #   - move
        #   - move + eval
        #   - move + concat
        #   - eval
        #   - concat
        # We need something to separate them: None (as a header of each move)
        self.__full_history.append(None)
        new_x, new_y = self.__move(x, y, direction)

        if direction in (Direction.LEFT, Direction.RIGHT):
            plus_minus = add if direction == Direction.RIGHT else sub
            if (concat_res := self.__concat_numbers_handler(new_x, plus_minus(new_x, 1), new_y)) is not None:
                self.__history.append((x, y, direction))
                return concat_res
            elif (val_res := self.__eval_numbers_handler(plus_minus(new_x, 1), new_y)) is not None:
                self.__history.append((x, y, direction))
                return val_res

        if (x, y) != (new_x, new_y):  # This move makes a change
            self.__history.append((x, y, direction))
        else:  # Nothing got changed
            self.__full_history.pop()  # Pop `None` that we appended earlier
        return new_x, new_y

    def __concat_numbers_handler(self, from_x: int, to_x: int, y: int) -> Union[None, Tuple[int, int]]:
        # `from_x` and `y` are valid for sure
        if to_x < 0 or to_x >= self.__PUZZLE_LENGTH or \
                not self.__is_number(self[y][from_x]) or \
                not self.__is_number(self[y][to_x]):
            return None

        return self.__concat_numbers(from_x, to_x, y)

    def __eval_numbers_handler(self, symbol_x: int, y: int) -> Union[None, Tuple[int, int]]:
        val1_x = symbol_x - 1
        val2_x = symbol_x + 1
        if val1_x < 0 or val1_x >= self.__PUZZLE_LENGTH or val2_x < 0 or val2_x >= self.__PUZZLE_LENGTH or \
                not self.__is_number(self[y][val1_x]) or \
                not self.__is_symbol(self[y][symbol_x]) or \
                not self.__is_number(self[y][val2_x]):
            return None

        try:
            return self.__eval_numbers(val1_x, symbol_x, val2_x, y)
        except ArithmeticError:  # divided by 0, not divisible, subtract from a number that is larger than itself
            return None

    def get_pieces(self) -> Set[Tuple[int, int]]:
        """Get all movable puzzle pieces in the puzzle.

        :return: a set of (x, y) coordinates
        :rtype: Set[Tuple[int, int]]
        """
        return copy(self.__pieces)  # No need `deepcopy` here, since tuples are immutable

    def is_solved(self) -> bool:
        """Check whether the puzzle is solved.

        :return: state of the puzzle
        :rtype: bool
        """
        if len(elements := self.get_pieces()) != 1:
            return False
        x, y = elements.pop()
        return self[y][x] == self.target

    def get_history(self) -> List[Tuple[int, int, Direction]]:
        """Get history of moves.

        :return: a list of moves that have been made
        :rtype: List[Tuple[int, int, Direction]]
        """
        return copy(self.__history)  # No need `deepcopy` here, since tuples are immutable

    def reset(self) -> None:
        """Reset the puzzle to the initial, same as calling `undo` method infinite times.

        :return: None
        """
        self.undo(len(self.__full_history))

    def restore_state_to(self, history: List[Tuple[int, int, Direction]]) -> None:
        # Parameter validation
        for record in history:
            if not (isinstance(record, tuple) and len(record) == 3 and
                    isinstance(record[0], int) and isinstance(record[1], int) and
                    isinstance(record[2], Direction) and 0 <= record[0] < self.__PUZZLE_LENGTH and
                    0 <= record[1] <= self.__PUZZLE_WIDTH):
                raise ValueError("malformed history")

        longest_common_prefix_length = None
        for longest_common_prefix_length, (this, that) in enumerate(zip_longest(self.__history, history)):
            if this != that:
                break

        if longest_common_prefix_length is not None:
            self.undo(len(self.__history) - longest_common_prefix_length)
            for args in history[longest_common_prefix_length:]:
                self.move(*args)

    def undo(self, move_count: int = 1) -> None:
        """Return the state of the puzzle to `move_count` number of moves before.

        :param move_count: the number of steps to undo, default to 1
        :type move_count: int, non-negative
        :return: None
        :raises ValueError: invalid `move_count`
        """
        # Parameter validation
        if not isinstance(move_count, int) or move_count < 0:
            raise ValueError(f"'move_count' should be a non-negative integer, not {move_count}")

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
                        self[from_y][from_x], self[to_y][to_x] = self[to_y][to_x], 0.1
                        self.__pieces.add((from_x, from_y))
                        self.__pieces.remove((to_x, to_y))
                    case "concat":
                        val1, val2, from_x, to_x, y = args
                        self[y][from_x], self[y][to_x] = val1, val2
                        self.__pieces.add((from_x, y))
                    case "eval":
                        val1, symbol, val2, leftmost_x, rightmost_x, y = args
                        self[y][leftmost_x], self[y][leftmost_x + 1], self[y][rightmost_x] \
                            = val1, symbol, val2
                        self.__pieces.add((leftmost_x, y))
                        self.__pieces.add((rightmost_x, y))
            self.__history.pop()
