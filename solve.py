from collections import deque
from copy import copy
from itertools import chain

from number_puzzle import Direction


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

        xs = (puzzle.history[-1][0], puzzle._ShuZiMiTi__full_history[-1][3])
        ys = (puzzle.history[-1][1], puzzle._ShuZiMiTi__full_history[-1][4])
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
