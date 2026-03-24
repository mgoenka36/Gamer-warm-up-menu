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
