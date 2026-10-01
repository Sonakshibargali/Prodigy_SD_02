"""
game.py - Core game logic for Number Guessing Game.
Maintains isolation from Flask web framework for testability and modularity.
"""

import random
from typing import Any, Dict, Optional, Tuple


class NumberGuessingGame:
    """Encapsulates the rules and state of a number guessing game."""

    DEFAULT_MIN = 1
    DEFAULT_MAX = 100

    def __init__(
        self,
        min_val: int = DEFAULT_MIN,
        max_val: int = DEFAULT_MAX,
        target_number: Optional[int] = None,
        attempts: int = 0,
        is_game_over: bool = False,
        history: Optional[list] = None,
    ) -> None:
        if min_val >= max_val:
            raise ValueError("min_val must be strictly less than max_val.")

        self.min_val = min_val
        self.max_val = max_val
        self.attempts = attempts
        self.is_game_over = is_game_over
        self.history = list(history) if history is not None else []

        if target_number is not None:
            if not (min_val <= target_number <= max_val):
                raise ValueError(
                    f"target_number ({target_number}) must be between {min_val} and {max_val}."
                )
            self.target_number = target_number
        else:
            self.target_number = random.randint(self.min_val, self.max_val)

    def validate_guess(self, raw_guess: Any) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Validates user input.
        Returns:
            (is_valid, parsed_integer, error_message)
        """
        if raw_guess is None or raw_guess == "":
            return False, None, "Please enter a number."

        # Reject booleans (which are instances of int in Python)
        if isinstance(raw_guess, bool):
            return False, None, "Please enter a valid integer."

        # Parse number
        try:
            if isinstance(raw_guess, float):
                if not raw_guess.is_integer():
                    return False, None, "Please enter a whole number without decimals."
                guess_int = int(raw_guess)
            elif isinstance(raw_guess, str):
                raw_trimmed = raw_guess.strip()
                if not raw_trimmed:
                    return False, None, "Please enter a number."
                # Check for float string like '4.5'
                if "." in raw_trimmed:
                    f_val = float(raw_trimmed)
                    if not f_val.is_integer():
                        return False, None, "Please enter a whole number without decimals."
                    guess_int = int(f_val)
                else:
                    guess_int = int(raw_trimmed)
            else:
                guess_int = int(raw_guess)
        except (ValueError, TypeError):
            return False, None, "Please enter a valid number."

        if guess_int < self.min_val or guess_int > self.max_val:
            return (
                False,
                None,
                f"Number must be between {self.min_val} and {self.max_val}.",
            )

        return True, guess_int, None

    def make_guess(self, raw_guess: Any) -> Dict[str, Any]:
        """
        Processes a guess and evaluates against target_number.
        Returns a status dictionary.
        """
        if self.is_game_over:
            return {
                "success": False,
                "status": "game_over",
                "message": "Game is already finished. Please play again.",
                "attempts": self.attempts,
                "is_game_over": True,
            }

        is_valid, guess_int, error_message = self.validate_guess(raw_guess)
        if not is_valid:
            return {
                "success": False,
                "status": "invalid",
                "message": error_message,
                "attempts": self.attempts,
                "is_game_over": False,
            }

        self.attempts += 1

        if guess_int < self.target_number:
            status = "too_low"
            message = "Too low! Try again."
        elif guess_int > self.target_number:
            status = "too_high"
            message = "Too high! Try again."
        else:
            status = "correct"
            message = "🎉 Correct!"
            self.is_game_over = True

        history_entry = {
            "guess": guess_int,
            "status": status,
            "message": message,
            "attempt": self.attempts,
        }
        self.history.append(history_entry)

        response = {
            "success": True,
            "status": status,
            "message": message,
            "guess": guess_int,
            "attempts": self.attempts,
            "is_game_over": self.is_game_over,
            "history": self.history,
        }

        if self.is_game_over:
            response["target"] = self.target_number

        return response

    def reset(self, new_target: Optional[int] = None) -> None:
        """Resets the game state and generates a new target number."""
        self.attempts = 0
        self.is_game_over = False
        self.history = []
        if new_target is not None:
            if not (self.min_val <= new_target <= self.max_val):
                raise ValueError(
                    f"new_target ({new_target}) must be between {self.min_val} and {self.max_val}."
                )
            self.target_number = new_target
        else:
            self.target_number = random.randint(self.min_val, self.max_val)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes game state for session storage."""
        return {
            "min_val": self.min_val,
            "max_val": self.max_val,
            "target_number": self.target_number,
            "attempts": self.attempts,
            "is_game_over": self.is_game_over,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NumberGuessingGame":
        """Reconstructs game instance from session dictionary."""
        return cls(
            min_val=data.get("min_val", cls.DEFAULT_MIN),
            max_val=data.get("max_val", cls.DEFAULT_MAX),
            target_number=data.get("target_number"),
            attempts=data.get("attempts", 0),
            is_game_over=data.get("is_game_over", False),
            history=data.get("history", []),
        )
