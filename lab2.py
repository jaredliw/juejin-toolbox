import numpy as np

from ultimate import Game, Direction


def pprint(mat):
    print(np.matrix(mat))


test_map = [
    [0.1, 0.1, 0.1],
    [0.1, 0.2, 0.1],
    [2, 0.4, 1],
    [1, 3, 0.1]
]
Game._Game__MAP_LENGTH = 3
Game._Game__MAP_WIDTH = 4

g = Game(test_map, 1)
pprint(g.game_map)
print()
commands = [
    # [2, 2, Direction.LEFT],
    [0, 2, Direction.UP],
    [0, 0, Direction.RIGHT],
    [2, 0, Direction.DOWN],
    [2, 1, Direction.LEFT],
    [2, 1, Direction.DOWN],
    [1, 3, Direction.LEFT],
    [1, 2, Direction.DOWN],
    [2, 2, Direction.DOWN],
    [2, 3, Direction.LEFT]
]

for x, y, d in commands:
    print(d)
    new_x, new_y = g.move(x, y, d)
    if (x, y) == (new_x, new_y):
        print("no change")
    else:
        print(new_x, new_y)
    pprint(g.game_map)
    print()

print(g.get_history())
g.undo(2)
print(g.get_history())
# g.undo(len(commands))
pprint(g.game_map)
# assert g.game_map == test_map
