from collections import deque
from copy import copy
from itertools import chain

from shuzimiti import Direction, ShuZiMiTi


def bfs(puzzle, val1, symbol, val2):
    count = 0

    def count_values():
        return len(puzzle.pieces[val1]), len(puzzle.pieces[symbol]), len(puzzle.pieces[val2]), len(puzzle.pieces[ans])

    def is_step_completed():
        after_counts = count_values()
        # ans check
        if after_counts[3] != initial_counts[3] + 1:
            return False
        # symbol check
        if symbol != 0.7 and after_counts[1] != initial_counts[1] - 1:
            return False
        # vals check
        if val1 == val2:
            if after_counts[0] != initial_counts[0] - 2:
                return False
        else:
            if after_counts[0] != initial_counts[0] - 1 or \
                    after_counts[2] != initial_counts[2] - 1:
                return False
        return True

    def flatten_2d(arr):
        return chain(*arr)

    ans = ShuZiMiTi.calc(val1, symbol, val2)
    initial_counts = count_values()
    to_do = deque([copy(puzzle.history)])

    while to_do:
        history = to_do.popleft()
        puzzle.restore_state_to(history)
        for x, y in flatten_2d(puzzle.pieces.values()):
            for direction in Direction:
                count += 1
                moved_x, moved_y = puzzle.move(x, y, direction)
                if x == moved_x and y == moved_y:
                    continue
                if is_step_completed():
                    print(count)
                    return

                new_history = copy(history)
                new_history.append((x, y, direction))
                to_do.append(new_history)
                puzzle.undo()
