import numpy as np

from ultimate import Game, Direction


def pprint(mat):
    print(np.matrix(mat))


min_map = [
    [0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1],
    [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1],
    [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1],
    [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1],
    [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1],
    [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1],
    [1, 0.2, 0.1, 0.1, 0.1, 0.2, 1]
]
# Game._Game__MAP_LENGTH = 3
# Game._Game__MAP_WIDTH = 3

g = Game(min_map, 11)
pprint(g.game_map)
print()
command = [
    [0, 6, Direction.UP],
    [0, 0, Direction.RIGHT],
    [2, 0, Direction.DOWN],
    [2, 6, Direction.RIGHT],
    [4, 6, Direction.UP],

    [6, 6, Direction.UP],
    [6, 0, Direction.LEFT]
]

for c in command:
    print(c[2])
    print(g.move(*c))
    pprint(g.game_map)
    print()
# for s in [(2, 0, Direction.DOWN), (1, 1, Direction.DOWN), (0, 2, Direction.RIGHT)]:
#     g.move(*s)
#     print(np.matrix(g.game_map))
#
# print(g.is_success())
# print(g.get_elements())
# print(g.game_map[2][1])
