"""Conway's game of life but with some extra sauce to enable WAR!"""
from loguru import logger

DEFAULT_BOARD_SIZE_X = 127
DEFAULT_BOARD_SIZE_Y = 131

PLAYER_1 = 0
PLAYER_2 = 1

PLAYER_1_COLOR = (255, 0, 0)
PLAYER_2_COLOR = (0, 0, 255)

PLAYER_1_START_POINT = (20, 20)
PLAYER_2_START_POINT = (DEFAULT_BOARD_SIZE_X - 20, DEFAULT_BOARD_SIZE_Y - 20)

class Player:
    def __init__(self, color, start_point):
        self.color = color
        self.start_point = start_point
        self.energy = 0.0

class CellState:
    def __init__(self, alive=False, immortal=False, crop_level=2.0 / (2**4), owner=None):
        self.alive = alive
        self.immortal = immortal
        self.crop_level = crop_level
        self.owner = owner

class GameState:


    def __init__(self, board=None):
        self.players = [
            Player(PLAYER_1_COLOR, PLAYER_1_START_POINT),
            Player(PLAYER_2_COLOR, PLAYER_2_START_POINT),
        ]
        if board is not None:
            self.board = board
            self.board_size_y = len(self.board)
            self.board_size_x = len(self.board[0])
        else:
            self.board = [
                [CellState() for _ in range(DEFAULT_BOARD_SIZE_Y)]
                for _ in range(DEFAULT_BOARD_SIZE_X)
            ]
            self.board_size_y = len(self.board)
            self.board_size_x = len(self.board[0])
            self.init_players()
        self.board_size_y = len(self.board)
        self.board_size_x = len(self.board[0])

    def init_players(self):
        for player in self.players:
            self.board[player.start_point[0]][player.start_point[1]].owner = player
            self.board[player.start_point[0]][player.start_point[1]].alive = True
            self.board[player.start_point[0]][player.start_point[1]].immortal = True
        self.update()
        self.update()

    def update_ownership_around_cell(self, x, y):
        """Update the ownership of the cells around a cell"""
        for i in range(-1, 2):
            for j in range(-1, 2):
                cell = self.board[(x + i) % self.board_size_x][(y + j) % self.board_size_y]
                cell.owner = self.board[x][y].owner


    def update_cell(self, x, y):
        """
        Update the state of a cell following the rules of conway's game of life.
        with the additional rules of war!
        """

        def count_friendly_neighbors(x, y, player):
            """Count neighbors and wrap around the board"""
            count = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    cell = self.board[(x + i) % self.board_size_x][(y + j) % self.board_size_y]
                    if cell.alive and cell.owner == player:
                        count += 1
            return count

        def fight_unfriendly_neighbors(x, y, player):
            """Kill unfriendly neighbors and wrap around the board"""
            if self.board[x][y].owner is None:
                return False
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    neighbor_cell = self.board[(x + i) % self.board_size_x][
                        (y + j) % self.board_size_y
                    ]
                    if neighbor_cell.alive and neighbor_cell.owner is not None and neighbor_cell.owner != player:
                        logger.info(f"Player {player} is fighting player {neighbor_cell.owner}")
                        neighbor_cell.alive = False
                        self.board[x][y].alive = False
                        return True
            return False
        
        def update_ownership_around_cell(x, y):
            """Update the ownership of the cells around a cell"""
            # Whoever has the most friendly neighbors gets the cell
            player_counts = [0 for _ in range(len(self.players))]
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    cell = self.board[(x + i) % self.board_size_x][(y + j) % self.board_size_y]
                    if cell.alive:
                        player_counts[self.players.index(cell.owner)] += 1
            # If there is a tie, the cell remains with the current owner
            current_owner_count = player_counts[self.players.index(cell.owner)] if cell.owner is not None else 0
            for i in range(len(self.players)):
                if player_counts[i] > current_owner_count:
                    cell.owner = self.players[i]


        cell = self.board[x][y]
        # If the cell is not alive and has a crop level less than 2, double the crop level
        if not cell.alive and cell.crop_level < 2 and cell.owner is not None:
            cell.crop_level = cell.crop_level * 2
        fight_unfriendly_neighbors(x, y, cell.owner)
        friendly_neighbors = count_friendly_neighbors(x, y, cell.owner)
        if cell.immortal:
            pass
        elif cell.alive:
            # The cell dies if it has less than 2 friendly neighbors
            if friendly_neighbors < 2:
                cell.alive = False
            # The cell dies if it has more than 3 friendly neighbors
            elif friendly_neighbors > 3:
                cell.alive = False
        else:
            # The cell comes to life if it has exactly 3 friendly neighbors
            if friendly_neighbors == 3:
                cell.alive = True

        if cell.owner is not None and cell.alive:
            cell.owner.energy += cell.crop_level
            cell.crop_level = 2.0 / (2**4)
        update_ownership_around_cell(x, y)


    def update(self):
        """Update the board"""
        for x in range(self.board_size_x):
            for y in range(self.board_size_y):
                self.update_cell(x, y)
        return self.board

    def generate_cell_color(self, x, y):
        """Generate the color of a cell"""
        color = (50, 50, 50)
        cell = self.board[x][y]
        if cell.alive:
            color = cell.owner.color
        color = (color[0], color[1] + ((255 / 2) * cell.crop_level), color[2])
        return color

    def generate_cell_border_color(self, x, y):
        """Generate the border color of a cell"""
        color = (150, 150, 150)
        cell = self.board[x][y]
        if cell.owner is not None:
            color = cell.owner.color
        return color

    def board_to_html(self):
        """Convert the board to an html string."""
        html = "<style>table {border-collapse: collapse;} td {padding: 0;}</style><table>"
        for y in range(self.board_size_y):
            html += "<tr>"
            for x in range(self.board_size_x):
                color = self.generate_cell_color(x, y)
                border_color = self.generate_cell_border_color(x, y)
                internal_div = f"<div hx-trigger='click' hx-post='/update_cell?x={x}&y={y}' style='height:5px;width:5px'></div>"
                if self.board[x][y].owner is None or self.board[x][y].immortal:
                    internal_div = "<div style='height:5px;width:5px'></div>"
                html += f"<td style='min-width=5px; min-height=5px; background-color:rgb({color[0]},{color[1]},{color[2]}); border: 1px solid rgb({border_color[0]},{border_color[1]},{border_color[2]});'>{internal_div}</td>"
            html += "</tr>"
        html += "</table>"
        return html

    def flip_cell(self, x, y):
        """Flip the state of a cell."""
        self.board[x][y].alive = not self.board[x][y].alive
        return self.board[x][y].alive
