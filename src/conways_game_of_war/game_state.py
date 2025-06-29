"""Conway's game of life but with some extra sauce to enable WAR!"""

import random
from dataclasses import dataclass

from loguru import logger

DEFAULT_BOARD_SIZE_X = 127
DEFAULT_BOARD_SIZE_Y = 131

PLAYER_1 = 0
PLAYER_2 = 1

PLAYER_1_COLOR = (255, 0, 0)
PLAYER_2_COLOR = (0, 0, 255)

PLAYER_1_START_POINT = (20, 20)
PLAYER_2_START_POINT = (DEFAULT_BOARD_SIZE_X - 20, DEFAULT_BOARD_SIZE_Y - 20)


@dataclass
class Player:
    """Represents a player in the game."""

    color: tuple
    start_point: tuple
    energy: float = 0.0

    def get_energy_level(self):
        """Return the player's energy level as a string."""
        return f"Energy: {self.energy}"


@dataclass
class CellState:
    """Represents the state of a cell in the game."""

    alive: bool = False
    immortal: bool = False
    crop_level: float = 2.0 / (2**4)
    owner: Player = None
    friendly_neighbors: int = 0


class AIPlayer(Player):
    """Represents an AI player in the game."""

    def make_move(self, game_state):
        """Determine the AI's move."""
        pass


class EasyAIPlayer(AIPlayer):
    """Represents an easy AI player in the game."""

    def make_move(self, game_state):
        """Make a random move."""
        empty_cells = [
            (x, y)
            for x in range(game_state.board_size_x)
            for y in range(game_state.board_size_y)
            if not game_state.board[x][y].alive
        ]
        if empty_cells:
            x, y = random.choice(empty_cells)
            game_state.flip_cell(x, y)


class MediumAIPlayer(AIPlayer):
    """Represents a medium AI player in the game."""

    def make_move(self, game_state):
        """Make a move targeting specific areas of the board."""
        # Implement a more advanced strategy here
        pass


class HardAIPlayer(AIPlayer):
    """Represents a hard AI player in the game."""

    def make_move(self, game_state):
        """Make a move targeting the opponent's weak spots."""
        # Implement a more advanced strategy here
        pass


class GameState:
    """Represents the state of the game board."""

    def __init__(
        self,
        board=None,
        board_size_x=DEFAULT_BOARD_SIZE_X,
        board_size_y=DEFAULT_BOARD_SIZE_Y,
    ):
        self.players = [
            Player(PLAYER_1_COLOR, PLAYER_1_START_POINT),
            Player(PLAYER_2_COLOR, PLAYER_2_START_POINT),
        ]
        self.ai_player = None
        if board is not None:
            self.board = board
            self.board_size_y = len(self.board)
            self.board_size_x = len(self.board[0])
        else:
            self.board = [
                [CellState() for _ in range(board_size_x)] for _ in range(board_size_y)
            ]
            self.board_size_y = len(self.board)
            self.board_size_x = len(self.board[0])
            self.init_players()
        self.board_size_x = len(self.board)
        logger.debug(f"Board size x: {self.board_size_x}")
        self.board_size_y = len(self.board[0])
        logger.debug(f"Board size y: {self.board_size_y}")
        # ensure that the board is a rectangle
        for row in self.board:
            assert len(row) == self.board_size_y

    def init_players(self):
        """Initialize the players on the board."""
        for player in self.players:
            self.board[player.start_point[0]][player.start_point[1]].owner = player
            self.board[player.start_point[0]][player.start_point[1]].alive = True
            self.board[player.start_point[0]][player.start_point[1]].immortal = True

    def update_ownership_around_cell(self, x, y):
        """Update the ownership of the cells around a cell."""
        # Whoever has the most friendly neighbors gets the cell
        player_counts = [0 for _ in range(len(self.players))]
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                loop_cell = self.board[(x + i) % self.board_size_x][
                    (y + j) % self.board_size_y
                ]
                if loop_cell.alive and loop_cell.owner is not None:
                    player_counts[self.players.index(loop_cell.owner)] += 1
        # If there is a tie, the cell remains with the current owner
        cell = self.board[x][y]
        current_owner_count = (
            player_counts[self.players.index(cell.owner)]
            if cell.owner is not None
            else 0
        )
        for i in range(len(self.players)):
            if player_counts[i] > current_owner_count:
                cell.owner = self.players[i]

    def count_friendly_neighbors(self, x, y, player):
        """Count neighbors and wrap around the board."""
        count = 0
        for i, j in [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]:
            if len(self.board) <= (x + i) % self.board_size_x:
                logger.error(f"Index out of range: {(x + i) % self.board_size_x}")
            if len(self.board[0]) <= (y + j) % self.board_size_y:
                logger.error(f"Index out of range: {(y + j) % self.board_size_y}")
            cell = self.board[(x + i) % self.board_size_x][(y + j) % self.board_size_y]
            if cell.alive and cell.owner == player:
                count += 1
        return count

    def update_friend_counts(self):
        """Update the number of friendly neighbors for each cell."""
        for x in range(self.board_size_x):
            for y in range(self.board_size_y):
                self.board[x][y].friendly_neighbors = self.count_friendly_neighbors(
                    x, y, self.board[x][y].owner
                )

    def update_cell(self, x, y):
        """
        Update the state of a cell following the rules of conway's game of life.
        with the additional rules of war!
        """

        def fight_unfriendly_neighbors(x, y, player):
            """Kill unfriendly neighbors and wrap around the board."""
            if self.board[x][y].owner is None:
                return False
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    neighbor_cell = self.board[(x + i) % self.board_size_x][
                        (y + j) % self.board_size_y
                    ]
                    if (
                        neighbor_cell.alive
                        and neighbor_cell.owner is not None
                        and neighbor_cell.owner != player
                    ):
                        logger.info(
                            f"Player {player} is fighting player {neighbor_cell.owner}"
                        )
                        neighbor_cell.alive = False
                        self.board[x][y].alive = False
                        return True
            return False

        cell = self.board[x][y]
        # If the cell is not alive and has a crop level less than 2, double the crop level
        if not cell.alive and cell.crop_level < 2 and cell.owner is not None:
            cell.crop_level = cell.crop_level * 2
        fight_unfriendly_neighbors(x, y, cell.owner)
        friendly_neighbors = cell.friendly_neighbors
        if cell.immortal:
            pass
        elif cell.alive:
            # The cell dies if it has less than 2 friendly neighbors
            if friendly_neighbors < 2:
                logger.debug(
                    f"Cell at {x}, {y} is lonely :( with {friendly_neighbors} friendly neighbors"
                )
                cell.alive = False
            # The cell dies if it has more than 3 friendly neighbors
            elif friendly_neighbors > 3:
                logger.debug(
                    f"Cell at {x}, {y} is overpopulated with {friendly_neighbors} friendly neighbors"
                )
                cell.alive = False
        else:
            # The cell comes to life if it has exactly 3 friendly neighbors
            if friendly_neighbors == 3:
                logger.debug(f"Cell at {x}, {y} is coming to life")
                cell.alive = True

        if cell.owner is not None and cell.alive:
            cell.owner.energy += cell.crop_level
            cell.crop_level = 2.0 / (2**4)
        self.update_ownership_around_cell(x, y)

    def update(self):
        """Update the board."""
        self.update_friend_counts()
        for x in range(self.board_size_x):
            for y in range(self.board_size_y):
                self.update_cell(x, y)
        if self.ai_player:
            self.ai_player.make_move(self)
        return self.board

    def generate_cell_color(self, x, y):
        """Generate the color of a cell."""
        color = (50, 50, 50)
        cell = self.board[x][y]
        if cell.alive and cell.owner is not None:
            color = cell.owner.color
        color = (color[0], color[1] + ((255 / 2) * cell.crop_level), color[2])
        return color

    def generate_cell_border_color(self, x, y):
        """Generate the border color of a cell."""
        color = (150, 150, 150)
        cell = self.board[x][y]
        if cell.owner is not None:
            color = cell.owner.color
        return color

    def board_to_html(self):
        """Convert the board to an html string."""
        html = "<div id='game'><style>table {border-collapse: collapse;} td {padding: 0;}</style><table>"
        for y in range(self.board_size_y):
            html += "<tr>"
            for x in range(self.board_size_x):
                color = self.generate_cell_color(x, y)
                border_color = self.generate_cell_border_color(x, y)
                internal_div = (
                    f"<div hx-trigger='click' hx-post='/update_cell?x={x}&y={y}' "
                    "hx-target='#game' style='height:5px;width:5px'></div>"
                )
                if self.board[x][y].owner is None or self.board[x][y].immortal:
                    internal_div = "<div style='height:5px;width:5px'></div>"
                html += (
                    f"<td style='min-width=5px; min-height=5px; background-color:rgb("
                    f"{color[0]},{color[1]},{color[2]}); border: 1px solid rgb("
                    f"{border_color[0]},{border_color[1]},{border_color[2]});'>"
                    f"{internal_div}</td>"
                )
            html += "</tr>"
        html += "</table></div>"
        return html

    def flip_cell(self, x, y):
        """Flip the state of a cell."""
        if self.is_cell_owned_by_player(x, y):
            self.board[x][y].alive = not self.board[x][y].alive
        return self.board[x][y].alive

    def is_cell_owned_by_player(self, x, y):
        """Check if a cell is owned by the current player."""
        cell = self.board[x][y]
        return (
            cell.owner == self.players[PLAYER_1] or cell.owner == self.players[PLAYER_2]
        )
