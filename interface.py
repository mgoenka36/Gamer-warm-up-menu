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








#FILE 4 END
