import mysql.connector
from mysql.connector import Error
import hashlib


class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "focusquest"

    def connect_server(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password
        )

    def connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def initialize_database(self):
        """Create the FocusQuest database, tables, admin account and questions."""
        db = None
        cursor = None

        try:
            # Create database
            db = self.connect_server()
            cursor = db.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.close()
            db.close()

            # Connect to FocusQuest database
            db = self.connect()
            cursor = db.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(64) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Questions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    question_id INT AUTO_INCREMENT PRIMARY KEY,
                    question_text VARCHAR(500) NOT NULL,
                    option1 VARCHAR(200) NOT NULL,
                    option2 VARCHAR(200) NOT NULL,
                    option3 VARCHAR(200) NOT NULL,
                    option4 VARCHAR(200) NOT NULL,
                    correct_answer VARCHAR(200) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    difficulty VARCHAR(20) NOT NULL,
                    points INT DEFAULT 10
                )
            """)

            # Results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    result_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    difficulty VARCHAR(20) NOT NULL,
                    score INT NOT NULL,
                    total_questions INT NOT NULL,
                    percentage DECIMAL(5,2) NOT NULL,
                    attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                )
            """)

            # Create demo admin account
            admin_password = self.hash_password("admin123")
            cursor.execute(
                "SELECT user_id FROM users WHERE username=%s",
                ("admin",)
            )

            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    INSERT INTO users
                    (username, password, full_name, role)
                    VALUES (%s, %s, %s, %s)
                    """,
                    ("admin", admin_password, "FocusQuest Admin", "admin")
                )

            # Insert questions only when the table is empty
            cursor.execute("SELECT COUNT(*) FROM questions")
            count = cursor.fetchone()[0]

            if count == 0:
                questions = [
                    # Kids Puzzle - 10
                    (
                        "What is 20 + 15?",
                        "30", "35", "40", "45",
                        "35", "Kids Puzzle", "Easy", 10
                    ),
                    (
                        "What is 90 - 36?",
                        "54", "56", "64", "66",
                        "54", "Kids Puzzle", "Easy", 10
                    ),
                    (
                        "How many sides does a pentagon have?",
                        "4", "5", "6", "7",
                        "5", "Kids Puzzle", "Easy", 10
                    ),
                    (
                        "Find the next number: 2, 5, 8, 11, ?",
                        "12", "13", "14", "15",
                        "14", "Kids Puzzle", "Medium", 10
                    ),
                    (
                        "What is 7 x 9?",
                        "56", "63", "64", "72",
                        "63", "Kids Puzzle", "Medium", 10
                    ),
                    (
                        "How many days are there in a normal year?",
                        "360", "364", "365", "366",
                        "365", "Kids Puzzle", "Easy", 10
                    ),
                    (
                        "Which number is the odd one out: 10, 20, 25, 30?",
                        "10", "20", "25", "30",
                        "25", "Kids Puzzle", "Medium", 10
                    ),
                    (
                        "What is double of 35?",
                        "60", "65", "70", "75",
                        "70", "Kids Puzzle", "Easy", 10
                    ),
                    (
                        "How many edges does a cube have?",
                        "6", "8", "12", "16",
                        "12", "Kids Puzzle", "Medium", 10
                    ),
                    (
                        "What is 200 - 75?",
                        "115", "125", "135", "145",
                        "125", "Kids Puzzle", "Easy", 10
                    ),

                    # Reasoning - 10
                    (
                        "Find the next number: 7, 14, 28, 56, ?",
                        "84", "98", "112", "120",
                        "112", "Reasoning", "Medium", 10
                    ),
                    (
                        "Which letter comes next: C, F, I, L, ?",
                        "M", "N", "O", "P",
                        "O", "Reasoning", "Medium", 10
                    ),
                    (
                        "Which is the odd one out?",
                        "Piano", "Guitar", "Violin", "Painting",
                        "Painting", "Reasoning", "Easy", 10
                    ),
                    (
                        "Teacher is to Student as Doctor is to?",
                        "Patient", "Nurse", "Medicine", "Hospital",
                        "Patient", "Reasoning", "Easy", 10
                    ),
                    (
                        "Find the next number: 1, 2, 6, 24, ?",
                        "48", "96", "120", "144",
                        "120", "Reasoning", "Medium", 10
                    ),
                    (
                        "If TOP is coded as UPQ, how is SUN coded?",
                        "TVO", "TUO", "RTM", "TVN",
                        "TVO", "Reasoning", "Medium", 10
                    ),
                    (
                        "You face east and turn right. Which direction do you face now?",
                        "North", "South", "West", "East",
                        "South", "Reasoning", "Easy", 10
                    ),
                    (
                        "What is the opposite of Victory?",
                        "Win", "Defeat", "Success", "Honour",
                        "Defeat", "Reasoning", "Easy", 10
                    ),
                    (
                        "Which number is the odd one out: 8, 27, 64, 100?",
                        "8", "27", "64", "100",
                        "100", "Reasoning", "Medium", 10
                    ),
                    (
                        "Find the next number: 50, 45, 39, 32, ?",
                        "24", "25", "26", "27",
                        "24", "Reasoning", "Medium", 10
                    ),

                    # Aptitude - 10
                    (
                        "What is 18% of 50?",
                        "7", "8", "9", "10",
                        "9", "Aptitude", "Medium", 10
                    ),
                    (
                        "An item costing Rs.100 is sold for Rs.120. What is the profit percentage?",
                        "10%", "15%", "20%", "25%",
                        "20%", "Aptitude", "Easy", 10
                    ),
                    (
                        "What is the average of 12, 18, 24, 30 and 36?",
                        "21", "24", "27", "30",
                        "24", "Aptitude", "Easy", 10
                    ),
                    (
                        "What is the simple interest on Rs.800 at 5% per year for 3 years?",
                        "Rs.100", "Rs.120", "Rs.150", "Rs.200",
                        "Rs.120", "Aptitude", "Medium", 10
                    ),
                    (
                        "Convert 72 km/h into m/s.",
                        "15 m/s", "18 m/s", "20 m/s", "25 m/s",
                        "20 m/s", "Aptitude", "Medium", 10
                    ),
                    (
                        "Two numbers are in the ratio 3:5 and their sum is 40. What is the larger number?",
                        "15", "20", "25", "30",
                        "25", "Aptitude", "Medium", 10
                    ),
                    (
                        "Solve: 3x + 4 = 19. What is x?",
                        "3", "4", "5", "6",
                        "5", "Aptitude", "Medium", 10
                    ),
                    (
                        "What is the LCM of 6 and 8?",
                        "12", "24", "36", "48",
                        "24", "Aptitude", "Easy", 10
                    ),
                    (
                        "How many days are there in 3 weeks?",
                        "18", "20", "21", "24",
                        "21", "Aptitude", "Easy", 10
                    ),
                    (
                        "What is 1/4 + 1/4?",
                        "1/8", "1/4", "1/2", "1",
                        "1/2", "Aptitude", "Easy", 10
                    ),

                    # Programming - 10
                    (
                        "Which keyword is used to check another condition after if in Python?",
                        "else", "elif", "elseif", "switch",
                        "elif", "Programming", "Easy", 10
                    ),
                    (
                        "What is the output of print(10 / 4) in Python?",
                        "2", "2.0", "2.5", "3",
                        "2.5", "Programming", "Medium", 10
                    ),
                    (
                        "Which function returns the type of a variable in Python?",
                        "type()", "typeof()", "kind()", "class()",
                        "type()", "Programming", "Easy", 10
                    ),
                    (
                        "Which operator checks equality in Python?",
                        "=", "==", "!=", "=>",
                        "==", "Programming", "Easy", 10
                    ),
                    (
                        "What is the index of the first element in a Python list?",
                        "0", "1", "-1", "2",
                        "0", "Programming", "Easy", 10
                    ),
                    (
                        "Which list method removes and returns the last item?",
                        "pop()", "remove()", "delete()", "cut()",
                        "pop()", "Programming", "Medium", 10
                    ),
                    (
                        "What is the output of print(\"A\" + \"B\")?",
                        "AB", "A B", "A+B", "Error",
                        "AB", "Programming", "Easy", 10
                    ),
                    (
                        "Which keyword creates an anonymous function in Python?",
                        "def", "lambda", "anon", "func",
                        "lambda", "Programming", "Medium", 10
                    ),
                    (
                        "Which Python data structure stores key-value pairs?",
                        "List", "Tuple", "Dictionary", "Set",
                        "Dictionary", "Programming", "Easy", 10
                    ),
                    (
                        "What is the output of len([1, 2, 3, 4])?",
                        "3", "4", "5", "Error",
                        "4", "Programming", "Easy", 10
                    ),

                    # Interview - 10
                    (
                        "What does HR stand for in a company?",
                        "Human Resources", "High Rank", "Hiring Round", "Human Records",
                        "Human Resources", "Interview", "Easy", 10
                    ),
                    (
                        "Which SQL clause limits the number of rows returned?",
                        "LIMIT", "COUNT", "ROWS", "MAX",
                        "LIMIT", "Interview", "Medium", 10
                    ),
                    (
                        "What does CRUD stand for?",
                        "Create, Read, Update, Delete",
                        "Copy, Run, Undo, Drop",
                        "Create, Run, Use, Delete",
                        "Compile, Read, Update, Debug",
                        "Create, Read, Update, Delete", "Interview", "Easy", 10
                    ),
                    (
                        "What is the purpose of a resume?",
                        "To summarise your skills, education and experience",
                        "To list your favourite movies",
                        "To replace the interview",
                        "To apply for a bank loan",
                        "To summarise your skills, education and experience",
                        "Interview", "Easy", 10
                    ),
                    (
                        "What does the SQL COMMIT command do?",
                        "Saves changes permanently",
                        "Deletes a table",
                        "Undoes changes",
                        "Creates an index",
                        "Saves changes permanently", "Interview", "Medium", 10
                    ),
                    (
                        "Which of these is an operating system?",
                        "Windows", "Chrome", "Python", "Excel",
                        "Windows", "Interview", "Easy", 10
                    ),
                    (
                        "What does HTTP stand for?",
                        "HyperText Transfer Protocol",
                        "High Transfer Text Process",
                        "Hyper Tool Transfer Program",
                        "Host Text Transfer Protocol",
                        "HyperText Transfer Protocol", "Interview", "Easy", 10
                    ),
                    (
                        "Which SQL keyword removes duplicate rows from a result?",
                        "UNIQUE", "DISTINCT", "DIFFERENT", "SINGLE",
                        "DISTINCT", "Interview", "Medium", 10
                    ),
                    (
                        "What is a firewall mainly used for?",
                        "Filtering network traffic for security",
                        "Editing photos",
                        "Compiling code",
                        "Storing emails",
                        "Filtering network traffic for security",
                        "Interview", "Medium", 10
                    ),
                    (
                        "Why should you research a company before an interview?",
                        "To understand its work and answer confidently",
                        "To criticise the company",
                        "To ask for a higher salary",
                        "There is no need to",
                        "To understand its work and answer confidently",
                        "Interview", "Easy", 10
                    )
                ]

                cursor.executemany(
                    """
                    INSERT INTO questions
                    (
                        question_text, option1, option2, option3, option4,
                        correct_answer, category, difficulty, points
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    questions
                )

            db.commit()

        except Error as e:
            print("Database initialization error:", e)
            raise

        finally:
            if cursor is not None:
                cursor.close()
            if db is not None and db.is_connected():
                db.close()

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, username, password, full_name):
        db = self.connect()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (username, password, full_name)
                VALUES (%s, %s, %s)
                """,
                (username, self.hash_password(password), full_name)
            )
            db.commit()
            return True, "Registration successful."

        except Error as e:
            if e.errno == 1062:
                return False, "Username already exists."
            return False, str(e)

        finally:
            cursor.close()
            db.close()

    def login_user(self, username, password):
        db = self.connect()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT user_id, full_name, role
                FROM users
                WHERE username=%s AND password=%s
                """,
                (username, self.hash_password(password))
            )
            return cursor.fetchone()

        finally:
            cursor.close()
            db.close()

    def get_questions(self, category, difficulty):
        db = self.connect()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT question_id, question_text, option1, option2,
                       option3, option4, correct_answer, points
                FROM questions
                WHERE category=%s AND difficulty=%s
                ORDER BY question_id
                """,
                (category, difficulty)
            )
            return cursor.fetchall()

        finally:
            cursor.close()
            db.close()

    def save_result(
        self,
        user_id,
        category,
        difficulty,
        score,
        total_questions,
        percentage
    ):
        db = self.connect()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO results
                (
                    user_id, category, difficulty, score,
                    total_questions, percentage
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    category,
                    difficulty,
                    score,
                    total_questions,
                    percentage
                )
            )
            db.commit()

        finally:
            cursor.close()
            db.close()

    def get_history(self, user_id):
        db = self.connect()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT category, difficulty, score, total_questions,
                       percentage, attempt_date
                FROM results
                WHERE user_id=%s
                ORDER BY attempt_date DESC
                """,
                (user_id,)
            )
            return cursor.fetchall()

        finally:
            cursor.close()
            db.close()

    def add_question(self, data):
        db = self.connect()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO questions
                (
                    question_text, option1, option2, option3, option4,
                    correct_answer, category, difficulty, points
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                data
            )
            db.commit()

        finally:
            cursor.close()
            db.close()

    def delete_question(self, question_id):
        db = self.connect()
        cursor = db.cursor()

        try:
            cursor.execute(
                "DELETE FROM questions WHERE question_id=%s",
                (question_id,)
            )
            db.commit()

        finally:
            cursor.close()
            db.close()

    def get_all_questions(self):
        db = self.connect()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT question_id, question_text, category,
                       difficulty, correct_answer, points
                FROM questions
                ORDER BY question_id
                """
            )
            return cursor.fetchall()

        finally:
            cursor.close()
            db.close()


# Optional direct test
if __name__ == "__main__":
    database = Database()
    database.initialize_database()
    print("FocusQuest database initialized successfully.")
    print("Demo login: admin / admin123")
 