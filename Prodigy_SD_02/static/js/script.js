/**
 * script.js - Client-side interaction for Number Guessing Game.
 * Handles asynchronous guess evaluation, history rendering, and game resets.
 */

document.addEventListener("DOMContentLoaded", () => {
    const guessForm = document.getElementById("guessForm");
    const guessInput = document.getElementById("guessInput");
    const guessBtn = document.getElementById("guessBtn");
    const feedback = document.getElementById("feedback");
    const attemptsCount = document.getElementById("attemptsCount");
    const quickResetBtn = document.getElementById("quickResetBtn");
    
    const historyContainer = document.getElementById("historyContainer");
    const historyList = document.getElementById("historyList");

    const winState = document.getElementById("winState");
    const finalAttempts = document.getElementById("finalAttempts");
    const targetNumber = document.getElementById("targetNumber");
    const playAgainBtn = document.getElementById("playAgainBtn");

    /**
     * Updates the feedback message and styling.
     */
    function setFeedback(message, type = "") {
        if (!message) {
            feedback.textContent = "";
            feedback.className = "feedback-msg idle";
            return;
        }

        let prefix = "";
        if (type === "too_high") {
            prefix = "↑ ";
        } else if (type === "too_low") {
            prefix = "↓ ";
        } else if (type === "invalid" || type === "error") {
            prefix = "⚠️ ";
        }

        feedback.textContent = prefix + message;
        feedback.className = `feedback-msg ${type}`;
    }

    /**
     * Renders previous guesses history chips.
     */
    function renderHistory(history) {
        if (!historyList || !historyContainer) return;

        if (!history || history.length === 0) {
            historyContainer.classList.add("hidden");
            historyList.innerHTML = "";
            return;
        }

        historyContainer.classList.remove("hidden");
        historyList.innerHTML = "";

        history.forEach((item) => {
            const chip = document.createElement("span");
            chip.className = `history-chip chip-${item.status}`;
            const symbol = item.status === "too_high" ? "↑" : item.status === "too_low" ? "↓" : "✓";
            chip.textContent = `${item.guess} ${symbol}`;
            historyList.appendChild(chip);
        });
    }

    /**
     * Handles guess submission.
     */
    async function handleGuess(event) {
        event.preventDefault();

        const rawValue = guessInput.value.trim();
        if (!rawValue) {
            setFeedback("Please enter a number.", "invalid");
            guessInput.focus();
            return;
        }

        const numericGuess = Number(rawValue);
        if (isNaN(numericGuess)) {
            setFeedback("Please enter a valid number.", "invalid");
            guessInput.focus();
            return;
        }

        // Disable button during request
        guessBtn.disabled = true;

        try {
            const response = await fetch("/guess", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify({ guess: numericGuess }),
            });

            const data = await response.json();

            // Update attempts count
            if (data.attempts !== undefined) {
                attemptsCount.textContent = data.attempts;
            }

            // Render guess history chips
            if (data.history) {
                renderHistory(data.history);
            }

            if (data.is_game_over && data.status === "correct") {
                // Show victory state
                finalAttempts.textContent = data.attempts;
                if (targetNumber && data.target) {
                    targetNumber.textContent = data.target;
                }
                guessForm.classList.add("hidden");
                winState.classList.remove("hidden");
                playAgainBtn.focus();
            } else {
                // Show feedback (too_high, too_low, invalid, etc.)
                setFeedback(data.message, data.status);
                guessInput.value = "";
                guessInput.focus();
            }
        } catch (error) {
            console.error("Error making guess:", error);
            setFeedback("An error occurred. Please try again.", "error");
        } finally {
            guessBtn.disabled = false;
        }
    }

    /**
     * Resets the game to start over.
     */
    async function handleReset() {
        if (playAgainBtn) playAgainBtn.disabled = true;
        if (quickResetBtn) quickResetBtn.disabled = true;

        try {
            const response = await fetch("/reset", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            const data = await response.json();

            // Reset UI state
            attemptsCount.textContent = data.attempts || 0;
            setFeedback("");
            guessInput.value = "";
            renderHistory([]);

            winState.classList.add("hidden");
            guessForm.classList.remove("hidden");
            guessInput.focus();
        } catch (error) {
            console.error("Error resetting game:", error);
            setFeedback("Failed to reset game. Please refresh the page.", "error");
        } finally {
            if (playAgainBtn) playAgainBtn.disabled = false;
            if (quickResetBtn) quickResetBtn.disabled = false;
        }
    }

    // Event Listeners
    if (guessForm) {
        guessForm.addEventListener("submit", handleGuess);
    }

    if (playAgainBtn) {
        playAgainBtn.addEventListener("click", handleReset);
    }

    if (quickResetBtn) {
        quickResetBtn.addEventListener("click", handleReset);
    }
});
