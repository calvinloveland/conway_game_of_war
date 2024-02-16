from conways_game_of_war.game_state import GameState, Player, CellState

def string_to_board(string):
    """Convert a string to a board"""
    board = []
    for y, line in enumerate(string.split("\n")):
        for x, char in enumerate(line):
            if y == 0:
                board.append([])
            if char == "X":
                board[x].append(CellState(alive=True))
            else:
                board[x].append(CellState())
    return board

def test_game_update():
    """Test that a blinker works as expected
    0 1 0
    0 1 0
    0 1 0
    should become:
    0 0 0
    1 1 1
    0 0 0
    """
    board = string_to_board("0X0\n0X0\n0X0")
    game = GameState(board)
    game.update()
    game.update()