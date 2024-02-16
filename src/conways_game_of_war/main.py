import flask
from conways_game_of_war import game_state

app = flask.Flask(__name__)

GAME = game_state.GameState()

def main():
    app.run(debug=True)

@app.route('/')
def index():
    GAME.update()
    return flask.render_template('index.html')

@app.route('/game_state')
def get_game_state():
    return GAME.board_to_html()

@app.route('/update_cell', methods=['POST'])
def update_cell():
    x = int(flask.request.args.get('x'))
    y = int(flask.request.args.get('y'))
    GAME.flip_cell(x, y)
    return GAME.board_to_html()
