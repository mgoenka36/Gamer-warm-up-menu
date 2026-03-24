import random
from timeit import default_timer as timer
import tkinter as tk
import mysql.connector


class DatabaseManager:
    """Handles MySQL setup and score storage."""
    def __init__(self, host="localhost", user="root", password="admin", database="wpm_highscores"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None
        self._connect()
        self._setup_database()

    def _connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            auth_plugin="mysql_native_password"
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        self.cursor.execute(f"USE {self.database}")

    def _setup_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS wpm_scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                wpm FLOAT
            )
        ''')

    def insert_score(self, wpm):
        query = "INSERT INTO wpm_scores (wpm) VALUES (%s)"
        self.cursor.execute(query, (wpm,))
        self.conn.commit()

    def fetch_high_score(self):
        self.cursor.execute("SELECT MAX(wpm) FROM wpm_scores")
        result = self.cursor.fetchone()
        return result[0] if result and result[0] else None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


class TypingSpeedTest:
    """Main class for the typing speed test GUI and logic."""
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.words = self._load_words()
        self.start_time = None
        self.root = tk.Tk()
        self.root.geometry("450x200")
        self.root.title("Typing Speed Test")
        self._setup_start_screen()

    def _load_words(self):
        """Load the challenge words (including some fun trash-talk)."""
        return [
            "programming", "algorithm", "python", "variable", "loop", "function", "class",
            "gaming", "debugging", "syntax", "exception", "keyboard", "developer", "compile",
            "astronaut", "network", "hardware", "database", "query", "cursor", "commit",
            # Trash-talk inspired challenge words:
            "rekt", "noob", "ggwp", "ezclap", "tryhard", "bozo", "cringe", "toxic",
            "lagger", "bot", "camping", "sweaty", "carried", "grindset", "malfunction"
        ]

    def _setup_start_screen(self):
        label = tk.Label(self.root, text="Let's start playing...", font="times 20")
        label.place(x=10, y=50)

        start_button = tk.Button(self.root, text="Go", command=self._start_game, width=12, bg='grey')
        start_button.place(x=150, y=100)

    def _start_game(self):
        self.root.destroy()
        self._create_game_window()

    def _create_game_window(self):
        self.window = tk.Tk()
        self.window.geometry("450x200")
        self.window.title("Typing Test")

        self.current_word = random.choice(self.words)
        self.start_time = timer()

        word_label = tk.Label(self.window, text=self.current_word, font="times 20")
        word_label.place(x=150, y=10)

        instruction = tk.Label(self.window, text="Start Typing:", font="times 20")
        instruction.place(x=10, y=50)

        self.entry = tk.Entry(self.window)
        self.entry.place(x=280, y=55)
        self.entry.focus_set()

        done_button = tk.Button(self.window, text="Done", command=self._check_result, width=12, bg='grey')
        done_button.place(x=150, y=100)

        retry_button = tk.Button(self.window, text="Try Again", command=self._restart_game, width=12, bg='grey')
        retry_button.place(x=250, y=100)

        self.window.mainloop()

    def _check_result(self):
        typed_text = self.entry.get().strip()
        if typed_text == self.current_word:
            end_time = timer()
            elapsed = end_time - self.start_time
            wpm = 60 / elapsed
            print(f"Your WPM: {wpm:.2f}")
            self.db.insert_score(wpm)
            high_score = self.db.fetch_high_score()
            print(f"Personal Best: {high_score:.2f} WPM")
            self._show_result_message(f"Your WPM: {wpm:.2f}\nPersonal Best: {high_score:.2f}")
        else:
            self._show_result_message("Inaccurate Input. Try Again!")

    def _restart_game(self):
        self.window.destroy()
        self._create_game_window()

    def _show_result_message(self, message):
        result_window = tk.Tk()
        result_window.geometry("300x150")
        result_window.title("Result")

        msg_label = tk.Label(result_window, text=message, font="times 15", justify="center")
        msg_label.pack(pady=30)

        ok_button = tk.Button(result_window, text="OK", command=result_window.destroy, bg="grey", width=10)
        ok_button.pack()

        result_window.mainloop()

    def run(self):
        self.root.mainloop()


# --- Main Execution ---
if __name__ == "__main__":
    db_manager = DatabaseManager()
    game = TypingSpeedTest(db_manager)
    game.run()

    high_score = db_manager.fetch_high_score()
    if high_score:
        print(f"Personal best: {high_score:.2f} WPM")
    else:
        print("No value stored in the table.")

    db_manager.close()
