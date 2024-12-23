"""Main module for running the Conway's Game of War Flask application."""

import flask
from conways_game_of_war import game_state

app = flask.Flask(__name__)
app.secret_key = "supersecretkey"  # Replace with a secure key in production

GAME = game_state.GameState()
ZOOM_LEVEL = 1.0


def main():
    """Run the Flask application."""
    app.run(debug=True)


@app.route("/")
def index():
    """Render the index page with window dimensions and zoom level."""
    if "player" not in flask.session:
        return flask.redirect("/select_player")
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


@app.route("/select_player")
def select_player():
    """Render the player selection screen."""
    return flask.render_template("select_player.html")


@app.route("/set_player", methods=["POST"])
def set_player():
    """Set the selected player in the session."""
    player = flask.request.form.get("player")
    flask.session["player"] = player
    ai_difficulty = flask.request.form.get("ai_difficulty")
    flask.session["ai_difficulty"] = ai_difficulty
    player1_color = flask.request.form.get("player1_color")
    player2_color = flask.request.form.get("player2_color")
    flask.session["player1_color"] = player1_color
    flask.session["player2_color"] = player2_color
    return flask.redirect("/")


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


@app.route("/player_energy")
def player_energy():
    """Return the player's energy level as HTML."""
    player = flask.session.get("player")
    if player == "player1":
        energy_level = GAME.players[0].get_energy_level()
    elif player == "player2":
        energy_level = GAME.players[1].get_energy_level()
    else:
        energy_level = "Unknown player"
    return f"<div>{energy_level}</div>"


if __name__ == "__main__":
    main()
