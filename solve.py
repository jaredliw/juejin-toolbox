from collections import deque
from copy import copy
from itertools import chain
from typing import List, Literal, Generator, Tuple

from number_puzzle import Direction, NumberPuzzle


def find_valid_calculations(puzzle: NumberPuzzle) \
        -> Generator[List[Tuple[int, Literal[0.3, 0.4, 0.5, 0.6, 0.7], int]], None, None]:
    """Find all valid calculations that are able to solve the given puzzle.

    :param puzzle: A puzzle
    :type puzzle: NumberPuzzle
    :return: A generator, yield a valid calculation a time
    :rtype: Generator[List[Tuple[int, Literal[0.3, 0.4, 0.5, 0.6, 0.7], int]], None, None]
    """

    def _inner(_numbers, _symbols, target, history=None):
        if history is None:
            history = []
        if len(_numbers) == 1 and len(_symbols) == 0 and _numbers[0] == target:
            yield history
            return

        _symbols.extend([0.7] * (len(_numbers) - len(_symbols) - 1))
        for symbol in (0.3, 0.4, 0.5, 0.6, 0.7):
            if symbol not in _symbols:
                continue

            symbols_copied = copy(_symbols)
            symbols_copied.remove(symbol)
            for idx, num1 in enumerate(_numbers[:-1]):
                for num2 in _numbers[idx + 1:]:
                    for _ in range(2):
                        try:
                            result = NumberPuzzle.calc(num1, symbol, num2)
                        except ArithmeticError:
                            pass
                        else:
                            numbers_copied = copy(_numbers)
                            numbers_copied.remove(num1)
                            numbers_copied.remove(num2)
                            numbers_copied.append(result)

                            history_copied = copy(history)
                            history_copied.append((num1, symbol, num2))

                            yield from _inner(numbers_copied, symbols_copied, target, history_copied)

                        if symbol in (0.4, 0.6, 0.7) and num1 != num2:  # -, / and & do not obey commutative law
                            num1, num2 = num2, num1
                        else:
                            break

    if not isinstance(puzzle, NumberPuzzle):
        raise TypeError(f"{puzzle} is not a {type(NumberPuzzle).__name__}")

    numbers = []
    symbols = []
    for piece, coordinates in puzzle.pieces.items():
        if NumberPuzzle.is_number(piece):
            numbers.extend([piece] * len(coordinates))
        elif NumberPuzzle.is_symbol(piece):
            symbols.extend([piece] * len(coordinates))
    return _inner(numbers, symbols, puzzle.target)


def bfs(puzzle, val1, symbol, val2, state=1):
    def is_step_completed():
        if state == 1 and symbol != 0.7:
            for val1_x, val1_y in puzzle.pieces[val1]:
                for symbol_x, symbol_y in puzzle.pieces[symbol]:
                    if val1_y == symbol_y:
                        if symbol == 0.3 or symbol == 0.5:
                            if abs(val1_x - symbol_x) == 1:
                                return True
                        else:
                            if val1_x - symbol_x == -1:
                                return True
            return False
        else:
            if operands is None:
                return False
            elif operands[1] in (0.3, 0.5):
                if operands == (val1, symbol, val2) or operands == (val2, symbol, val1):
                    return True
            else:
                return operands == (val1, symbol, val2)

    def get_pieces():
        if len(puzzle.history) <= initial_history_length:
            return list(chain(*puzzle.pieces.values()))

        xs = (puzzle.history[-1][0], puzzle._NumberPuzzle__full_history[-1][3])
        ys = (puzzle.history[-1][1], puzzle._NumberPuzzle__full_history[-1][4])
        filtered_pieces = []
        for loc in chain(*puzzle.pieces.values()):
            if loc[0] in xs or loc[1] in ys:
                filtered_pieces.append(loc)
        return filtered_pieces

    count = 0
    to_do = deque([copy(puzzle.history)])
    initial_history_length = len(puzzle.history)

    while to_do:
        history = to_do.popleft()
        puzzle.restore_state_to(history)
        for x, y in get_pieces():
            for direction in Direction:
                count += 1
                (moved_x, moved_y), operands = puzzle.move(x, y, direction)
                if len(history) > 0 and moved_x == history[-1][0] and moved_y == history[-1][1]:
                    puzzle.undo()
                    continue
                if x == moved_x and y == moved_y:
                    continue
                if is_step_completed():
                    print(count)
                    if state == 1 and symbol != 0.7:
                        bfs(puzzle, val1, symbol, val2, state=2)
                    return

                new_history = copy(history)
                new_history.append((x, y, direction))
                to_do.append(new_history)
                puzzle.undo()
