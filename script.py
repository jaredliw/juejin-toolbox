from collections import deque
from copy import deepcopy

from shuzimiti import Direction, ShuZiMiTi

# map_ = [
#     [0.1,
#     0.1, 0.2, 0.3, 0.2, 19, 0.1],
#     [7, 0.1, 0.1, 0.6, 0.1, 0.1, 0.6],
#     [0.1, 0.2, 0.1, 0.1, 3, 0.2, 0.1],
#     [0.1, 0.1, 2, 0.1, 0.1, 0.1, 0.1],
#     [0.1, 0.6, 0.1, 17, 0.2, 0.1, 5],
#     [0.1, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1],
#     [11, 0.1, 0.2, 0.1, 13, 0.1, 0.1]
# ]
# # aim: 11 + 19
# target = 2
# g = Game(map_)

min_map = [
    [0.1, 0.1, 0.2, 0.3, 0.2, 19, 0.1],
    [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
    [0.1, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1],
    [0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
    [0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1],
    [0.1, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1],
    [11, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1]
]
MAX_DEPTH = 8

to_do = deque()
to_do.append((ShuZiMiTi(min_map, 30), 0))
from time import time

st = time()
count = 0
while to_do:
    game, depth = to_do.popleft()

    for x, y in game.get_pieces():
        for direction in Direction:
            count += 1
            game_clone = deepcopy(game)

            moved_x, moved_y = game_clone.move(x, y, direction)
            if x == moved_x and y == moved_y:
                continue
            if game_clone.is_solved():
                success_game = game_clone
                print(game_clone)
                print(game_clone.game_map)
                print(game_clone.get_history())
                print(f"{count=}")
                print(time() - st)
                exit()
            if depth + 1 > MAX_DEPTH:
                continue
            to_do.append((game_clone, depth + 1))
