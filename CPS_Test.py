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
