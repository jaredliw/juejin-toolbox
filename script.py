from api import JuejinGameSession
from number_puzzle import NumberPuzzle
from solve import find_valid_calculations, bfs

PPRINT_GRID_LEFT_RIGHT_PADDING = 1
FLOAT_TO_SYMBOL = {
    0.3: "+",
    0.4: "-",
    0.5: "*",
    0.6: "/",
    0.7: "&"
}


def pprint_puzzle(puzzle: NumberPuzzle) -> None:
    """Pretty Juejin Number Puzzle.

    :param puzzle: A puzzle
    :type puzzle: NumberPuzzle
    :return: None
    """
    if not isinstance(puzzle, NumberPuzzle):
        raise TypeError(f"{puzzle} is not a {NumberPuzzle.__name__}")

    def _format_piece(item):
        match item:
            case 0.1:
                return ""
            case 0.2:
                return "\u2588" * (max_cell_width - 2 * PPRINT_GRID_LEFT_RIGHT_PADDING)  # a solid black block
            case 0.3 | 0.4 | 0.5 | 0.6:
                return FLOAT_TO_SYMBOL[item]
            case _:
                return str(item)

    max_cell_width = max(map(lambda piece: len(str(piece)) if isinstance(piece, int) else -1, puzzle.pieces.keys()))
    max_cell_width += 2 * PPRINT_GRID_LEFT_RIGHT_PADDING

    for row in puzzle.puzzle:
        print("+" + "+".join("-" * max_cell_width for _ in range(puzzle.WIDTH)) + "+")
        print("|" + "|".join(_format_piece(item).center(max_cell_width) for item in row) + "|")
    print("+" + "+".join("-" * max_cell_width for _ in range(puzzle.WIDTH)) + "+")


if __name__ == "__main__":
    from time import time

    MY_SESSION = "xxx"
    session = JuejinGameSession(MY_SESSION)

    while True:
        data = session.fetch_level_data()
        start_time = time()

        np = NumberPuzzle(data["map"], data["target"])
        print("Level", data["round"])
        pprint_puzzle(np)
        print("Target:", data["target"])
        print()

        print("Calculations:")
        solution_generator = find_valid_calculations(np)
        solution = next(solution_generator, None)
        if solution is None:
            print("This puzzle is not solvable. Report this to the author if you think this is a bug.")
            exit()
        for num1, symbol, num2 in solution:
            print(num1, FLOAT_TO_SYMBOL[symbol], num2)
        print()

        print("Steps:")
        last_until = 0
        data_to_submit = []
        for step in solution:
            bfs(np, *step)
            for item in np.history[last_until:]:
                x, y, direction = np.decode_history_record(item)
                print(f"({x}, {y}) {direction.name}")
                data_to_submit.append([y, x, direction.name[0].lower()])
            last_until = len(np.history)
            print()
        print(session.submit_level(data_to_submit))
        print()

        end_time = time()
        print("Time taken:", end_time - start_time)
