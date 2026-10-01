"""
app.py - Flask Web Application for Number Guessing Game.
Provides RESTful API endpoints and server-rendered fallback for gameplay.
"""

import os
from flask import Flask, jsonify, render_template, request, session
from game import NumberGuessingGame

app = Flask(__name__)
# In production, this should be set from an environment variable
app.secret_key = os.environ.get("SECRET_KEY", "prodigy-sd-02-number-guessing-game-secret")


def get_current_game() -> NumberGuessingGame:
    """Retrieves the game instance from the Flask session or creates a new one."""
    game_data = session.get("game")
    if not game_data:
        game = NumberGuessingGame(min_val=1, max_val=100)
        session["game"] = game.to_dict()
        return game
    return NumberGuessingGame.from_dict(game_data)


def save_game(game: NumberGuessingGame) -> None:
    """Saves the current game state into the Flask session."""
    session["game"] = game.to_dict()


@app.route("/", methods=["GET"])
def index():
    """Renders the main game interface."""
    game = get_current_game()
    return render_template(
        "index.html",
        min_val=game.min_val,
        max_val=game.max_val,
        attempts=game.attempts,
        is_game_over=game.is_game_over,
        history=game.history,
    )


@app.route("/guess", methods=["POST"])
def guess():
    """
    Handles a user's guess submission.
    Supports both JSON payload (fetch/AJAX) and traditional form submission.
    """
    game = get_current_game()

    # Determine input from JSON or Form
    if request.is_json:
        data = request.get_json(silent=True) or {}
        raw_guess = data.get("guess")
    else:
        raw_guess = request.form.get("guess")

    result = game.make_guess(raw_guess)
    save_game(game)

    # Return JSON for AJAX requests or API clients
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        status_code = 200 if result.get("success") or result.get("status") in ["game_over", "invalid"] else 400
        return jsonify(result), status_code

    # Fallback to server-side render
    return render_template(
        "index.html",
        min_val=game.min_val,
        max_val=game.max_val,
        attempts=game.attempts,
        is_game_over=game.is_game_over,
        last_guess=raw_guess,
        message=result.get("message"),
        status=result.get("status"),
    )


@app.route("/reset", methods=["POST"])
def reset():
    """Resets the game state and generates a new target number."""
    game = get_current_game()
    game.reset()
    save_game(game)

    response_data = {
        "success": True,
        "status": "reset",
        "message": "Game has been reset. Guess a new number!",
        "attempts": game.attempts,
        "is_game_over": False,
        "min_val": game.min_val,
        "max_val": game.max_val,
    }

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(response_data), 200

    return render_template(
        "index.html",
        min_val=game.min_val,
        max_val=game.max_val,
        attempts=game.attempts,
        is_game_over=False,
    )


@app.route("/status", methods=["GET"])
def status():
    """Returns current sanitized game status for the active session."""
    game = get_current_game()
    return jsonify({
        "min_val": game.min_val,
        "max_val": game.max_val,
        "attempts": game.attempts,
        "is_game_over": game.is_game_over,
    }), 200


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
