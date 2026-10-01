"""
tests/test_app.py - Integration and Route tests for Flask Number Guessing Game.
"""

import json
import unittest
from app import app
from game import NumberGuessingGame


class TestFlaskIntegration(unittest.TestCase):
    """Integration tests for the Flask web application routes."""

    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key"
        self.client = app.test_client()

    def test_index_route(self):
        """Test GET / returns 200 and loads basic UI elements."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html_content = response.data.decode("utf-8")
        self.assertIn("Number Guessing Game", html_content)
        self.assertIn("Guess the number between 1–100", html_content)
        self.assertIn('id="guessInput"', html_content)
        self.assertIn("Play Again", html_content)

    def test_json_guess_low_high_and_correct(self):
        """Test sequential JSON guess requests within a single user session."""
        with self.client:
            # First initialize session
            self.client.get("/")

            # Intercept session to set deterministic target number 42
            with self.client.session_transaction() as sess:
                game = NumberGuessingGame(min_val=1, max_val=100, target_number=42)
                sess["game"] = game.to_dict()

            # 1. Guess too low (20)
            res1 = self.client.post(
                "/guess",
                data=json.dumps({"guess": 20}),
                content_type="application/json",
            )
            self.assertEqual(res1.status_code, 200)
            data1 = res1.get_json()
            self.assertTrue(data1["success"])
            self.assertEqual(data1["status"], "too_low")
            self.assertEqual(data1["message"], "Too low! Try again.")
            self.assertEqual(data1["attempts"], 1)
            self.assertFalse(data1["is_game_over"])

            # 2. Guess too high (80)
            res2 = self.client.post(
                "/guess",
                data=json.dumps({"guess": 80}),
                content_type="application/json",
            )
            self.assertEqual(res2.status_code, 200)
            data2 = res2.get_json()
            self.assertTrue(data2["success"])
            self.assertEqual(data2["status"], "too_high")
            self.assertEqual(data2["message"], "Too high! Try again.")
            self.assertEqual(data2["attempts"], 2)
            self.assertFalse(data2["is_game_over"])

            # 3. Guess correct number (42)
            res3 = self.client.post(
                "/guess",
                data=json.dumps({"guess": 42}),
                content_type="application/json",
            )
            self.assertEqual(res3.status_code, 200)
            data3 = res3.get_json()
            self.assertTrue(data3["success"])
            self.assertEqual(data3["status"], "correct")
            self.assertEqual(data3["message"], "🎉 Correct!")
            self.assertEqual(data3["attempts"], 3)
            self.assertTrue(data3["is_game_over"])

    def test_json_guess_validation_errors(self):
        """Test invalid inputs return informative error without advancing attempts."""
        with self.client:
            self.client.get("/")

            # Set target 50
            with self.client.session_transaction() as sess:
                sess["game"] = NumberGuessingGame(target_number=50).to_dict()

            # Out of bounds (< 1)
            res = self.client.post(
                "/guess",
                data=json.dumps({"guess": 0}),
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertFalse(data["success"])
            self.assertEqual(data["status"], "invalid")
            self.assertEqual(data["attempts"], 0)

            # Decimal
            res_dec = self.client.post(
                "/guess",
                data=json.dumps({"guess": 25.5}),
                content_type="application/json",
            )
            self.assertEqual(res_dec.status_code, 200)
            data_dec = res_dec.get_json()
            self.assertFalse(data_dec["success"])
            self.assertEqual(data_dec["status"], "invalid")
            self.assertEqual(data_dec["attempts"], 0)

    def test_reset_endpoint(self):
        """Test POST /reset generates a new game with 0 attempts."""
        with self.client:
            self.client.get("/")

            with self.client.session_transaction() as sess:
                game = NumberGuessingGame(target_number=50)
                game.make_guess(20)
                sess["game"] = game.to_dict()

            # Call reset endpoint
            res = self.client.post(
                "/reset",
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertTrue(data["success"])
            self.assertEqual(data["status"], "reset")
            self.assertEqual(data["attempts"], 0)
            self.assertFalse(data["is_game_over"])

            # Verify session was reset
            with self.client.session_transaction() as sess:
                new_game_dict = sess["game"]
                self.assertEqual(new_game_dict["attempts"], 0)
                self.assertFalse(new_game_dict["is_game_over"])

    def test_status_endpoint(self):
        """Test GET /status returns state without exposing target_number."""
        with self.client:
            self.client.get("/")
            with self.client.session_transaction() as sess:
                sess["game"] = NumberGuessingGame(target_number=99, attempts=3).to_dict()

            res = self.client.get("/status")
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data["attempts"], 3)
            self.assertNotIn("target_number", data)

    def test_form_submission_fallback(self):
        """Test traditional HTML form submission works for non-JS clients."""
        with self.client:
            self.client.get("/")
            with self.client.session_transaction() as sess:
                sess["game"] = NumberGuessingGame(target_number=50).to_dict()

            response = self.client.post("/guess", data={"guess": "30"})
            self.assertEqual(response.status_code, 200)
            html = response.data.decode("utf-8")
            self.assertIn("Too low! Try again.", html)
            self.assertIn("Attempts: <span id=\"attemptsCount\">1</span>", html)


if __name__ == "__main__":
    unittest.main()
