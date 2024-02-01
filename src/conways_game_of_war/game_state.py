"""Conway's game of life but with some extra sauce to enable WAR!"""

BOARD_SIZE_X = 127
BOARD_SIZE_Y = 131

PLAYER_1 = 0
PLAYER_2 = 1

PLAYER_1_COLOR = (255, 0, 0)
PLAYER_2_COLOR = (0, 0, 255)

PLAYER_1_START_POINT = (20,20)
PLAYER_2_START_POINT = (BOARD_SIZE_X - 20, BOARD_SIZE_Y - 20)



class GameState():

    class Player():
        def __init__(self, color, start_point):
            self.color = color
            self.start_point = start_point
            self.energy = 0.0

    class CellState():
        alive = False
        immortal = False
        crop_level = 2.0 / (2 ** 4)
        owner = None

    def __init__(self):
        self.board = [[GameState.CellState() for _ in range(BOARD_SIZE_X)] for _ in range(BOARD_SIZE_Y)]
        self.players = [GameState.Player(PLAYER_1_COLOR, PLAYER_1_START_POINT), GameState.Player(PLAYER_2_COLOR, PLAYER_2_START_POINT)]
        self.init_players()

    def init_players(self):
        for player in self.players:
            self.board[player.start_point[0]][player.start_point[1]].owner = player
            self.board[player.start_point[0]][player.start_point[1]].alive = True
            self.board[player.start_point[0]][player.start_point[1]].immortal = True

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
                    cell = self.board[(x + i) % BOARD_SIZE_X][(y + j) % BOARD_SIZE_Y]
                    if cell.alive and cell.owner == player:
                        count += 1
            return count

        def fight_unfriendly_neighbors(x, y, player):
            """Kill unfriendly neighbors and wrap around the board"""
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    neighbor_cell = self.board[(x + i) % BOARD_SIZE_X][(y + j) % BOARD_SIZE_Y]
                    if neighbor_cell.alive and neighbor_cell.owner != player:
                        neighbor_cell.alive = False
                        self.board[x][y].alive = False
                        return True
            return False

        cell = self.board[x][y]
        # If the cell is not alive and has a crop level less than 2, double the crop level
        if not cell.alive and cell.crop_level < 2 and cell.owner is not None:
            cell.crop_level = cell.crop_level * 2
        fight_unfriendly_neighbors(x, y, cell.owner)
        friendly_neighbors = count_friendly_neighbors(x, y, cell.owner)
        if cell.alive:
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
                if cell.owner is not None:
                    cell.owner += cell.crop_level
                cell.crop_level = 2.0 / (2 ** 4)
        # Whoever has the most friendly neighbors gets the cell
        player_counts = [0 for _ in range(len(self.players))]
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                cell = self.board[(x + i) % BOARD_SIZE_X][(y + j) % BOARD_SIZE_Y]
                if cell.alive:
                    player_counts[self.players.index(cell.owner)] += 1
        for i in range(len(self.players)):
            if player_counts[i] > player_counts[cell.owner]:
                cell.owner = self.players[i]
        

        
