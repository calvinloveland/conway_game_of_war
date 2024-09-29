"""Main module for running the Conway's Game of War Flask application."""

import flask
from conways_game_of_war import game_state

app = flask.Flask(__name__)

GAME = game_state.GameState()
ZOOM_LEVEL = 1.0


def main():
    """Run the Flask application."""
    app.run(debug=True)


@app.route("/")
def index():
    """Render the index page with window dimensions and zoom level."""
    window_width = flask.request.args.get("width", type=int, default=800)
    window_height = flask.request.args.get("height", type=int, default=600)
    zoom_level = flask.request.args.get("zoom", type=float, default=1.0)
    GAME.update()
    return flask.render_template(
        "index.html",
        window_width=window_width,
        window_height=window_height,
        zoom_level=zoom_level,
    )


@app.route("/game_state")
def get_game_state():
    """Return the current game state as HTML."""
    return GAME.board_to_html()


@app.route("/update_cell", methods=["POST"])
def update_cell():
    """Update the state of a cell and return the updated game state as HTML."""
    x = int(flask.request.args.get("x"))
    y = int(flask.request.args.get("y"))
    GAME.flip_cell(x, y)
    return GAME.board_to_html()


@app.route("/zoom", methods=["POST"])
def zoom():
    """Update the zoom level and return the updated game state as HTML."""
    zoom_level = float(flask.request.args.get("zoom"))
    global ZOOM_LEVEL
    ZOOM_LEVEL = zoom_level
    return GAME.board_to_html()


if __name__ == "__main__":
    main()
