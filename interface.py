
#FILE NUMBER 1 - save as: "interface.py"

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

#FILE 1 END
#FILE NUMBER 2 - save as: "Aim_Trainer.py"

import pygame
import math
import random
import sys
import time
import array
import mysql.connector


def at():
    pygame.init()

    # --- Setup ---
    width, height = 1600, 900
    display = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Aim Trainer")

    # Colors
    black = (0, 0, 0)
    white = (255, 255, 255)
    purple = (128, 0, 128)
    grey = (128, 128, 128)
    sky = (0, 0, 220)
    blue = (85, 206, 255)
    orange = (255, 127, 80)
    red = (200, 0, 0)
    light_red = (255, 0, 0)
    green = (0, 200, 0)
    light_green = (0, 255, 0)
    colors = [white, grey, purple, sky, blue, orange, red, light_red, green, light_green]

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 28, bold=True)
    big_font = pygame.font.SysFont("Arial", 44, bold=True)

    # --- Audio Setup ---
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        audio_ok = True
    except Exception:
        audio_ok = False

    def make_beep(frequency=880, duration_ms=100):
        """Generate a simple sine-wave beep as a pygame Sound."""
        if not audio_ok:
            return None
        sample_rate = 44100
        n_samples = int(sample_rate * duration_ms / 1000)
        buf = array.array("h")
        amplitude = 4096
        for i in range(n_samples):
            sample = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
            buf.append(sample)
        try:
            return pygame.mixer.Sound(buffer=buf)
        except Exception:
            return None

    hit_sound = make_beep(880, 100)
    miss_sound = make_beep(220, 100)

    # --- Game State ---
    hits = 0
    total_clicks = 0
    running = True

    # --- Timer ---
    start_ticks = pygame.time.get_ticks()
    elapsed_seconds = 0

    # --- UI Layout ---
    quit_button_rect = pygame.Rect(width - 160, 20, 120, 50)
    acc_text_x, acc_text_y = 20, 20
    acc_text_height = 40
    timer_text_x, timer_text_y = 20, 60

    # --- Target Generator ---
    def new_circle():
        """Generate new target away from quit and UI areas."""
        while True:
            cx = random.randint(40, width - 40)
            cy = random.randint(80, height - 40)
            r = random.randint(9, 13)
            target_rect = pygame.Rect(cx - r, cy - r, 2 * r, 2 * r)

            too_close_to_quit = target_rect.colliderect(quit_button_rect.inflate(40, 40))
            too_close_to_top = cy < acc_text_y + acc_text_height + 50
            if not (too_close_to_quit or too_close_to_top):
                return cx, cy, r, random.choice(colors)

    cx, cy, radius, color = new_circle()

    # --- Game Loop ---
    while running:
        display.fill(black)
        elapsed_ms = pygame.time.get_ticks() - start_ticks
        elapsed_seconds = elapsed_ms // 1000

        # Draw elements
        pygame.draw.circle(display, color, (cx, cy), radius)
        pygame.draw.rect(display, red, quit_button_rect, border_radius=8)
        quit_text = font.render("QUIT", True, white)
        display.blit(quit_text, (quit_button_rect.x + 25, quit_button_rect.y + 10))

        accuracy = (hits / total_clicks * 100) if total_clicks > 0 else 0
        acc_text = font.render(f"Accuracy: {accuracy:.1f}%", True, white)
        display.blit(acc_text, (acc_text_x, acc_text_y))

        mins = elapsed_seconds // 60
        secs = elapsed_seconds % 60
        timer_text = font.render(f"Time: {mins:02d}:{secs:02d}", True, white)
        display.blit(timer_text, (timer_text_x, timer_text_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos

                # If quit clicked → end game, don’t update accuracy
                if quit_button_rect.collidepoint(x, y):
                    running = False
                    break

                total_clicks += 1

                if math.hypot(x - cx, y - cy) <= radius:
                    hits += 1
                    if hit_sound:
                        hit_sound.play()
                    cx, cy, radius, color = new_circle()
                else:
                    if miss_sound:
                        miss_sound.play()

        pygame.display.update()
        clock.tick(60)

    # --- After quitting ---
    final_accuracy = (hits / total_clicks * 100) if total_clicks > 0 else 0
    played_time = elapsed_seconds

    # --- MySQL Handling ---
    high_score = final_accuracy
    db_message = ""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin"
        )
        cur = conn.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS aim_trainer_db;")
        conn.database = "aim_trainer_db"
        cur.execute("""
            CREATE TABLE IF NOT EXISTS aim_trainer_scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                accuracy FLOAT NOT NULL,
                play_time INT NOT NULL,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute(
            "INSERT INTO aim_trainer_scores (accuracy, play_time) VALUES (%s, %s);",
            (final_accuracy, played_time)
        )
        conn.commit()
        cur.execute("SELECT MAX(accuracy) FROM aim_trainer_scores;")
        high_score = cur.fetchone()[0]
        cur.close()
        conn.close()
        db_message = "Score saved successfully."
    except Exception:
        # Silent fail - no printed traceback or error line
        db_message = "Score not saved (DB unavailable)."

    # --- Exit Summary ---
    display.fill(black)
    title = big_font.render("Session Summary", True, white)
    acc_text = font.render(f"Final Accuracy: {final_accuracy:.1f}%", True, white)
    high_text = font.render(f"High Score: {high_score:.1f}%", True, white)
    time_text = font.render(f"Time Played: {played_time//60:02d}:{played_time%60:02d}", True, white)
    db_text = font.render(db_message, True, white)

    display.blit(title, (width//2 - title.get_width()//2, height//2 - 120))
    display.blit(acc_text, (width//2 - acc_text.get_width()//2, height//2 - 40))
    display.blit(high_text, (width//2 - high_text.get_width()//2, height//2 + 10))
    display.blit(time_text, (width//2 - time_text.get_width()//2, height//2 + 60))
    display.blit(db_text, (width//2 - db_text.get_width()//2, height//2 + 120))

    pygame.display.update()
    pygame.time.wait(4000)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    at()

#FILE 2 END
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
