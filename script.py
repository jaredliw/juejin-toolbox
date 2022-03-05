from collections import deque
from copy import copy
from itertools import chain

from shuzimiti import Direction


def bfs(puzzle, val1, symbol, val2):
    def is_step_completed():
        if operands is None:
            return False
        elif operands[1] in (0.3, 0.5):
            return operands == (val1, symbol, val2) or operands == (val2, symbol, val1)
        else:
            return operands == (val1, symbol, val2)

    count = 0
    to_do = deque([copy(puzzle.history)])

    while to_do:
        history = to_do.popleft()
        puzzle.restore_state_to(history)
        for x, y in list(chain(*puzzle.pieces.values())):
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
                    return

                new_history = copy(history)
                new_history.append((x, y, direction))
                to_do.append(new_history)
                puzzle.undo()
