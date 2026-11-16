
import os
import sys
import time
import random
import msvcrt

# Enable ANSI terminal support on Windows
os.system("")

WIDTH = 60
HEIGHT = 20
WIN_SCORE = 5
FPS = 60

PADDLE_SIZE = 4

player_y = HEIGHT // 2
ai_y = HEIGHT // 2

ball_x = WIDTH // 2
ball_y = HEIGHT // 2

ball_dx = random.choice([-1, 1])
ball_dy = random.choice([-0.5, 0.5])

player_score = 0
ai_score = 0

def reset_ball(direction):
    global ball_x, ball_y, ball_dx, ball_dy

    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_dx = direction
    ball_dy = random.choice([-0.5, 0.5])

def draw():
    os.system("cls" if os.name == "nt" else "clear")

    print("🏓 PONG CLI")
    print(f"PLAYER {player_score}  |  AI {ai_score}")
    print("W/S = MOVE | Q = QUIT")
    print("+" + "-" * WIDTH + "+")

    for y in range(HEIGHT):
        row = [" "] * WIDTH

        # Player paddle
        if 2 <= y < 2 + PADDLE_SIZE:
            row[1] = "|"

        # AI paddle
        if HEIGHT // 2 - PADDLE_SIZE // 2 <= y < HEIGHT // 2 + PADDLE_SIZE // 2:
            row[WIDTH - 2] = "|"

        # Ball
        if int(ball_y) == y:
            row[int(ball_x)] = "O"

        print("|" + "".join(row) + "|")

    print("+" + "-" * WIDTH + "+")

def input_handler():
    global player_y

    while msvcrt.kbhit():
        key = msvcrt.getch().decode(errors="ignore").lower()

        if key == "w":
            player_y = max(0, player_y - 1)

        elif key == "s":
            player_y = min(HEIGHT - PADDLE_SIZE, player_y + 1)

        elif key == "q":
            sys.exit()

def update():
    global ball_x, ball_y, ball_dx, ball_dy
    global ai_y, player_score, ai_score

    ball_x += ball_dx
    ball_y += ball_dy

    # Wall bounce
    if ball_y <= 0 or ball_y >= HEIGHT - 1:
        ball_dy *= -1

    # AI movement
    ai_center = ai_y + PADDLE_SIZE // 2

    if ai_center < ball_y:
        ai_y = min(HEIGHT - PADDLE_SIZE, ai_y + 0.35)
    elif ai_center > ball_y:
        ai_y = max(0, ai_y - 0.35)

    # Player collision
    if ball_x <= 2:
        if player_y <= ball_y <= player_y + PADDLE_SIZE:
            ball_dx *= -1.1
        else:
            ai_score += 1
            reset_ball(1)

    # AI collision
    if ball_x >= WIDTH - 3:
        if ai_y <= ball_y <= ai_y + PADDLE_SIZE:
            ball_dx *= -1.1
        else:
            player_score += 1
            reset_ball(-1)


def main():
    global player_score, ai_score

    try:
        while player_score < WIN_SCORE and ai_score < WIN_SCORE:
            input_handler()
            update()
            draw()
            time.sleep(1 / FPS)

        draw()
        print("\nGAME OVER!")

        if player_score > ai_score:
            print("YOU WIN!")
        else:
            print("AI WINS!")

        print(f"FINAL SCORE: {player_score} - {ai_score}")

    except KeyboardInterrupt:
        print("\nGame interrupted.")

    finally:
        print("\nThanks for playing!")
        
if __name__ == "__main__":
    main()
