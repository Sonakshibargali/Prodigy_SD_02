# 🎯 Number Guessing Game

> **Prodigy InfoTech — Software Development Internship | Task 02**

A simple and professional web-based Number Guessing Game built with **Python and Flask**. The game generates a random number between **1 and 100** and provides feedback until the user guesses the correct number.

## 🚀 Features

- Generates a random number between 1 and 100
- Provides **Too High** / **Too Low** feedback
- Tracks the number of attempts
- Displays a success message when the number is guessed
- Play Again option to start a new game
- Input validation and error handling
- Per-user game state using Flask sessions
- Responsive and minimal UI
- Unit and integration tests

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **State Management:** Flask Sessions
- **Testing:** Python `unittest`

## 📁 Project Structure

```text
Prodigy_SD_02/
├── app.py
├── game.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── tests/
    ├── __init__.py
    ├── test_game.py
    └── test_app.py
```

## ⚙️ Setup & Run

### 1. Clone the repository

```bash
git clone https://github.com/Sonakshibargali/Prodigy_SD_02.git
cd Prodigy_SD_02
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## 🧪 Run Tests

Run the complete test suite using:

```bash
python -m unittest discover -s tests
```

The tests cover game logic, input validation, attempt tracking, reset functionality, Flask routes, and session handling.

## 🎮 How to Play

1. Enter a number between **1 and 100**.
2. Click **Guess**.
3. Follow the **Too High** or **Too Low** feedback.
4. Continue guessing until you find the correct number.
5. The application displays the total number of attempts.
6. Click **Play Again** to start a new game.

## 👤 Author

**Sonakshi Bargali**

**Prodigy InfoTech — Software Development Internship**  
**Task 02: Number Guessing Game**
