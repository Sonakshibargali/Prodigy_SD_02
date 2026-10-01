"""
tests/test_game.py - Comprehensive Unit Tests for NumberGuessingGame logic.
"""

import unittest
from game import NumberGuessingGame


class TestNumberGuessingGame(unittest.TestCase):
    """Unit tests for the standalone NumberGuessingGame class."""

    def setUp(self):
        # Initialize a deterministic game with target number 50
        self.game = NumberGuessingGame(min_val=1, max_val=100, target_number=50)

    def test_default_initialization(self):
        """Test default game initialization within bounds."""
        game = NumberGuessingGame()
        self.assertEqual(game.min_val, 1)
        self.assertEqual(game.max_val, 100)
        self.assertTrue(1 <= game.target_number <= 100)
        self.assertEqual(game.attempts, 0)
        self.assertFalse(game.is_game_over)

    def test_invalid_range_raises_error(self):
        """Test that invalid min_val and max_val configurations raise ValueError."""
        with self.assertRaises(ValueError):
            NumberGuessingGame(min_val=100, max_val=1)
        with self.assertRaises(ValueError):
            NumberGuessingGame(min_val=50, max_val=50)

    def test_invalid_target_number_raises_error(self):
        """Test that target number outside bounds raises ValueError."""
        with self.assertRaises(ValueError):
            NumberGuessingGame(min_val=1, max_val=100, target_number=0)
        with self.assertRaises(ValueError):
            NumberGuessingGame(min_val=1, max_val=100, target_number=101)

    def test_validation_empty_or_none(self):
        """Test validation fails for None, empty, or whitespace-only values."""
        for empty_val in [None, "", "   "]:
            res = self.game.make_guess(empty_val)
            self.assertFalse(res["success"])
            self.assertEqual(res["status"], "invalid")
            self.assertIn("Please enter a number", res["message"])
            self.assertEqual(self.game.attempts, 0)

    def test_validation_boolean_rejected(self):
        """Test booleans are rejected even though bool is a subclass of int in Python."""
        res_true = self.game.make_guess(True)
        self.assertFalse(res_true["success"])
        self.assertEqual(res_true["status"], "invalid")

        res_false = self.game.make_guess(False)
        self.assertFalse(res_false["success"])
        self.assertEqual(res_false["status"], "invalid")
        self.assertEqual(self.game.attempts, 0)

    def test_validation_non_integer(self):
        """Test rejection of non-numeric strings and decimal numbers."""
        invalid_inputs = ["abc", "12a", "forty-two", 25.5, "25.5"]
        for bad_input in invalid_inputs:
            res = self.game.make_guess(bad_input)
            self.assertFalse(res["success"])
            self.assertEqual(res["status"], "invalid")
            self.assertEqual(self.game.attempts, 0)

    def test_validation_out_of_bounds(self):
        """Test numbers outside range [1, 100] are rejected without incrementing attempts."""
        out_of_bounds = [0, -10, 101, 999]
        for num in out_of_bounds:
            res = self.game.make_guess(num)
            self.assertFalse(res["success"])
            self.assertEqual(res["status"], "invalid")
            self.assertIn("between 1 and 100", res["message"])
            self.assertEqual(self.game.attempts, 0)

    def test_valid_too_low_guess(self):
        """Test guess lower than target number returns 'too_low' and increments attempts."""
        res = self.game.make_guess(30)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "too_low")
        self.assertEqual(res["message"], "Too high! Try again." if 30 > 50 else "Too low! Try again.")
        self.assertEqual(res["attempts"], 1)
        self.assertEqual(self.game.attempts, 1)
        self.assertFalse(self.game.is_game_over)

    def test_valid_too_high_guess(self):
        """Test guess higher than target number returns 'too_high' and increments attempts."""
        res = self.game.make_guess(75)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "too_high")
        self.assertEqual(res["message"], "Too high! Try again.")
        self.assertEqual(res["attempts"], 1)
        self.assertEqual(self.game.attempts, 1)
        self.assertFalse(self.game.is_game_over)

    def test_valid_correct_guess(self):
        """Test correct guess returns 'correct', marks game_over, and tracks final attempts."""
        self.game.make_guess(20)  # attempt 1
        self.game.make_guess(80)  # attempt 2
        res = self.game.make_guess(50)  # attempt 3 (correct)

        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "correct")
        self.assertEqual(res["message"], "🎉 Correct!")
        self.assertEqual(res["attempts"], 3)
        self.assertTrue(res["is_game_over"])
        self.assertTrue(self.game.is_game_over)

    def test_guess_after_game_over(self):
        """Test that making guesses after game is over is blocked."""
        self.game.make_guess(50)  # game ends
        self.assertTrue(self.game.is_game_over)

        res = self.game.make_guess(50)
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "game_over")
        self.assertIn("Game is already finished", res["message"])
        self.assertEqual(self.game.attempts, 1)

    def test_reset_game(self):
        """Test reset functionality clears attempts and sets new target."""
        self.game.make_guess(25)
        self.game.make_guess(50)
        self.assertTrue(self.game.is_game_over)
        self.assertEqual(self.game.attempts, 2)

        self.game.reset(new_target=77)
        self.assertEqual(self.game.attempts, 0)
        self.assertFalse(self.game.is_game_over)
        self.assertEqual(self.game.target_number, 77)

        # Confirm new game plays with new target
        res = self.game.make_guess(50)
        self.assertEqual(res["status"], "too_low")
        self.assertEqual(self.game.attempts, 1)

    def test_serialization(self):
        """Test to_dict and from_dict state serialization."""
        self.game.make_guess(20)
        game_dict = self.game.to_dict()

        reloaded = NumberGuessingGame.from_dict(game_dict)
        self.assertEqual(reloaded.target_number, self.game.target_number)
        self.assertEqual(reloaded.attempts, self.game.attempts)
        self.assertEqual(reloaded.is_game_over, self.game.is_game_over)
        self.assertEqual(reloaded.min_val, self.game.min_val)
        self.assertEqual(reloaded.max_val, self.game.max_val)


if __name__ == "__main__":
    unittest.main()
