import numpy as np

from ultimate import Game, Direction


def pprint(mat):
    print(np.matrix(mat))


test_map = [
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

g = Game(test_map, 11)
pprint(g.game_map)
print()
commands = [
    [0, 6, Direction.UP],
    [0, 0, Direction.RIGHT],
    [2, 0, Direction.DOWN],
    [2, 6, Direction.RIGHT],
    [4, 6, Direction.UP],

    [6, 6, Direction.UP],
    [6, 0, Direction.LEFT]
]

for c in commands:
    print(c[2])
    print(g.move(*c))
    pprint(g.game_map)
    print()

g.reset()
pprint(g.game_map)
assert g.game_map == test_map
