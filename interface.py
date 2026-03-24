import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import mysql.connector


# --- Game launching ---
def launch_game(file_name):
    """Launch one of the game files."""
    if not os.path.exists(file_name):
        messagebox.showerror("Error", f"Game file '{file_name}' not found!")
        return
    subprocess.Popen([sys.executable, file_name])


# --- Interface ---
def main():
    root = tk.Tk()
    root.title("🎮 Game Launcher")
    root.geometry("600x450")
    root.configure(bg="#121212")

    title = tk.Label(
        root,
        text="Select a Game",
        font=("Arial", 22, "bold"),
        fg="#50C878",
        bg="#121212"
    )
    title.pack(pady=20)

    # Game buttons
    games = [
        ("Aim Trainer", "Aim_Trainer.py", "#00BFFF"),
        ("Typing Speed Test", "TPS_Test.py", "#FFA500"),
        ("CPS Clicker", "CPS_Test.py", "#FF4C4C")
    ]

    for name, file, color in games:
        frame = tk.Frame(root, bg="#1E1E1E", pady=10)
        frame.pack(pady=10, fill="x", padx=40)

        tk.Label(
            frame,
            text=name,
            font=("Arial", 16, "bold"),
            fg=color,
            bg="#1E1E1E"
        ).pack(side="left", padx=20)

        tk.Button(
            frame,
            text="Play",
            bg=color,
            fg="black",
            font=("Arial", 12, "bold"),
            width=8,
            command=lambda f=file: launch_game(f)
        ).pack(side="right", padx=20)

    # Exit button
    tk.Button(
        root,
        text="Exit",
        command=root.destroy,
        bg="#444",
        fg="white",
        font=("Arial", 12, "bold"),
        width=15
    ).pack(pady=30)

    root.mainloop()


if __name__ == "__main__":
    main()


#FILE NUMBER 3 - save as: "CPS_Test"

import mysql.connector
import tkinter as tk
import os
import sys


class CPSClicker:
    """Click-per-second test with MySQL integration and in-window results."""

    def __init__(self):
        self.db_params = {
            "host": "localhost",
            "user": "root",
            "passwd": "admin",
            "auth_plugin": "mysql_native_password"
        }
        self._setup_database()

        self.time_up = False
        self.counter = 0
        self.duration = 5  # seconds

        self.root = tk.Tk()
        self.root.geometry("500x500")
        self.root.title("CLICKS PER SECOND")
        self.root.configure(bg="#0A0A0A")

        self._show_start_screen()
        self.root.mainloop()

    # ---------------- Database ----------------

    def _setup_database(self):
        """Ensure DB and table exist."""
        try:
            conn = mysql.connector.connect(**self.db_params)
            cur = conn.cursor()
            cur.execute("CREATE DATABASE IF NOT EXISTS highscore_db")
            cur.execute("USE highscore_db")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    score INT
                )
            """)
            conn.commit()
            conn.close()
        except mysql.connector.Error as e:
            print("DB setup error:", e)

    def _save_score(self, score):
        """Save current score and return high score."""
        try:
            conn = mysql.connector.connect(database="highscore_db", **self.db_params)
            cur = conn.cursor()
            cur.execute("INSERT INTO high_scores (score) VALUES (%s)", (score,))
            conn.commit()
            cur.execute("SELECT MAX(score) FROM high_scores")
            high = cur.fetchone()[0]
            conn.close()
            return high
        except mysql.connector.Error as e:
            print("DB save error:", e)
            return None

    # ---------------- GUI Setup ----------------

    def _show_start_screen(self):
        lbl_title = tk.Label(
            self.root,
            text="The Click's\nPer Second \nTest",
            font=('Roboto', 20),
            bg="#0A0A0A",
            fg="#50C878"
        )
        lbl_title.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        btn_start = tk.Button(
            self.root,
            text="Continue",
            bg="#0A0A0A",
            fg="#50C878",
            command=lambda: self._start_game(lbl_title, btn_start)
        )
        btn_start.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    def _start_game(self, lbl_title, btn_start):
        lbl_title.destroy()
        btn_start.destroy()
        self._setup_game_ui()
        self._start_timer()

    def _setup_game_ui(self):
        lbl_instructions = tk.Label(
            self.root,
            text="When You Are Ready\nClick The Button As Fast As Possible\nFor 5 Seconds!",
            bg="#0A0A0A",
            fg="#ED2939",
            font=("Helvetica", 14, "bold italic")
        )
        lbl_instructions.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        btn_exit = tk.Button(
            self.root,
            text="EXIT",
            bg="#0A0A0A",
            fg="#ED2939",
            command=self._restart_program
        )
        btn_exit.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        self.btn_click = tk.Button(
            self.root,
            text="CLICK!",
            font=("Arial", 70),
            bg="#0A0A0A",
            fg="#FEDE00",
            command=self._register_click
        )
        self.btn_click.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    # ---------------- Game Logic ----------------

    def _register_click(self):
        if not self.time_up:
            self.counter += 1

    def _start_timer(self):
        self.root.after(self.duration * 1000, self._end_game)

    def _end_game(self):
        self.time_up = True
        cps = round(self.counter / self.duration, 2)
        high = self._save_score(self.counter)

        for widget in self.root.winfo_children():
            widget.destroy()

        # Display results within same window
        tk.Label(
            self.root,
            text="Session Summary",
            font=("Arial", 26, "bold"),
            fg="#50C878",
            bg="#0A0A0A"
        ).pack(pady=30)

        tk.Label(
            self.root,
            text=f"Total Clicks: {self.counter}",
            font=("Arial", 18),
            fg="white",
            bg="#0A0A0A"
        ).pack(pady=10)

        tk.Label(
            self.root,
            text=f"Clicks Per Second: {cps}",
            font=("Arial", 18),
            fg="white",
            bg="#0A0A0A"
        ).pack(pady=10)

        tk.Label(
            self.root,
            text=f"High Score: {high if high else 'N/A'}",
            font=("Arial", 18),
            fg="#FEDE00",
            bg="#0A0A0A"
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Play Again",
            bg="#0A0A0A",
            fg="#50C878",
            font=("Arial", 14, "bold"),
            command=self._restart_program
        ).pack(pady=30)

    def _restart_program(self):
        os.execl(sys.executable, sys.executable, *sys.argv)


if __name__ == "__main__":
    CPSClicker()

#FILE 3 END
#FILE 4 - SAVE AS: "TPS_Test.py"

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

#FILE 4 END
