# FocusQuest

FocusQuest is an interactive puzzle and learning challenge platform developed using Python, Tkinter and MySQL.

## Main Features

- User registration and login
- Kids Puzzle category
- Aptitude category
- Reasoning category
- Programming category
- Interview category
- Easy, Medium and Hard difficulty levels
- 15-second question timer
- Automatic score calculation
- Percentage calculation
- MySQL result storage
- User progress/history
- Admin question management
- Password hashing using SHA-256

## Technologies

- Python
- Tkinter
- MySQL
- MySQL Connector/Python
- VS Code
- XAMPP

## Installation

1. Install Python.
2. Install XAMPP.
3. Start MySQL from XAMPP.
4. Open the FocusQuest folder in VS Code.
5. Open the VS Code terminal.
6. Run:

```bash
pip install -r requirements.txt
```

7. Run:

```bash
python __main__.py
```

The application automatically creates the `focusquest` database and required tables.

## Demo Admin

Username: `admin`

Password: `admin123`

Use the admin account to open the Question Manager.

## Project Flow

Registration/Login
        ↓
Dashboard
        ↓
Select Category
        ↓
Select Difficulty
        ↓
Quiz
        ↓
Answer Validation
        ↓
Score Calculation
        ↓
Result
        ↓
Progress Stored in MySQL
