from collections import deque
from copy import copy
from itertools import chain
from time import time

from shuzimiti import Direction, ShuZiMiTi


def bfs(puzzle, val1, symbol, val2):
    def count_values():
        pieces = puzzle.get_pieces()
        return len(pieces[val1]), len(pieces[symbol]), len(pieces[val2]), len(pieces[ans])

    def is_step_completed():
        after_counts = count_values()
        # ans check
        if after_counts[3] != initial_counts[3] + 1:
            return False
        # symbol check
        if symbol != 0.7:
            if after_counts[1] != initial_counts[1] - 1:
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
    to_do = deque([puzzle.get_history()])

    while to_do:
        history = to_do.popleft()
        puzzle.restore_state_to(history)
        for x, y in flatten_2d(puzzle.get_pieces().values()):
            for direction in Direction:
                moved_x, moved_y = puzzle.move(x, y, direction)
                if x == moved_x and y == moved_y:
                    continue
                if is_step_completed():
                    return

                new_history = copy(history)
                new_history.append((x, y, direction))
                to_do.append(new_history)
                puzzle.undo()


if __name__ == "__main__":
    from numpy import matrix, set_printoptions

    set_printoptions(suppress=True)


    def pprint(arr):
        print(matrix(arr))


    test_map = [
        [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 4],
        [5, 0.1, 0.6, 0.1, 0.1, 0.1, 0.1],
        [0.1, 0.2, 0.1, 12, 0.1, 0.1, 0.1],
        [0.1, 0.2, 0.1, 0.1, 0.1, 0.6, 0.1],
        [0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 5],
        [0.1, 0.1, 0.1, 0.1, 0.1, 6, 0.1],
        [0.1, 0.1, 0.3, 0.1, 0.1, 0.1, 0.1]
    ]
    test_map = [
        [0.1, 0.1, 0.2, 0.3, 0.2, 19, 0.1],
        [7, 0.1, 0.1, 0.6, 0.1, 0.1, 0.6],
        [0.1, 0.2, 0.1, 0.1, 3, 0.2, 0.1],
        [0.1, 0.1, 2, 0.1, 0.1, 0.1, 0.1],
        [0.1, 0.6, 0.1, 17, 0.2, 0.1, 5],
        [0.1, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1],
        [11, 0.1, 0.2, 0.1, 13, 0.1, 0.1]
    ]
    test_puzzle = ShuZiMiTi(test_map, 22)

    start_time = time()
    # bfs(test_puzzle, 5, 0.6, 5)
    # print(1)
    # bfs(test_puzzle, 1, 0.7, 6)
    # print(2)
    # bfs(test_puzzle, 12, 0.3, 4)
    # print(3)
    # bfs(test_puzzle, 16, 0.6, 16)
    # print(4)
    bfs(test_puzzle, 13, 0.7, 2)
    print(test_puzzle.get_history())
    # bfs(test_puzzle, 5, 0.7, 7)
    # print(test_puzzle.get_history())
    # bfs(test_puzzle, 132, 0.6, 11)
    # print(test_puzzle.get_history())
    # bfs(test_puzzle, 12, 0.6, 3)
    # print(test_puzzle.get_history())
    # bfs(test_puzzle, 57, 0.6, 19)
    # print(test_puzzle.get_history())
    # bfs(test_puzzle, 4, 0.7, 3)
    # print(test_puzzle.get_history())
    # bfs(test_puzzle, 17, 0.3, 43)
    # print(test_puzzle.get_history())
    #
    # bfs(test_puzzle, 2, 0.7, 2)
    end_time = time()

    pprint(test_puzzle.puzzle)
    answer = test_puzzle.get_history()
    for args in answer:
        print(*args)

    print("Time taken:", end_time - start_time)

    # Validate answer
    # new_puzzle = ShuZiMiTi(test_map, 30)
    # for args in answer:
    #     new_puzzle.move(*args)
    # assert new_puzzle.is_solved()
