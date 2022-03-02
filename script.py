from collections import deque
from copy import copy
from time import time

from shuzimiti import Direction, ShuZiMiTi


def bfs(puzzle):
    to_do = deque([[]])

    while to_do:
        history = to_do.popleft()
        puzzle.restore_state_to(history)
        for x, y in puzzle.get_pieces():
            for direction in Direction:
                moved_x, moved_y = puzzle.move(x, y, direction)
                if x == moved_x and y == moved_y:
                    continue
                if puzzle.is_solved():
                    return

                new_history = copy(history)
                new_history.append((x, y, direction))
                to_do.append(new_history)
                puzzle.undo()


if __name__ == "__main__":
    from numpy import matrix


    def pprint(arr):
        print(matrix(arr))


    test_map = [
        [0.1, 0.1, 0.2, 0.3, 0.2, 19, 0.1],
        [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        [0.1, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1],
        [0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        [0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1],
        [0.1, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1],
        [11, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1]
    ]
    test_puzzle = ShuZiMiTi(test_map, 30)

    start_time = time()
    bfs(test_puzzle)
    end_time = time()

    pprint(test_puzzle.puzzle)
    answer = test_puzzle.get_history()
    for args in answer:
        print(*args)

    print("Time taken:", end_time - start_time)

    # Validate answer
    new_puzzle = ShuZiMiTi(test_map, 30)
    for args in answer:
        new_puzzle.move(*args)
    assert new_puzzle.is_solved()
