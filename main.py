import curses
import time

def main(stdscr):
    # Setup terminal screen
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)  # Controls game speed (lower = faster)

    sh, sw = stdscr.getmaxyx()

    # Ensure terminal is large enough
    if sh < 15 or sw < 40:
        stdscr.nodelay(False)
        stdscr.addstr(0, 0, "Terminal too small! Resize to at least 40x15 and restart.")
        stdscr.getch()
        return

    # Paddle settings
    paddle_h = 4
    left_y = sh // 2 - paddle_h // 2
    right_y = sh // 2 - paddle_h // 2

    # Ball settings
    ball_y, ball_x = sh // 2, sw // 2
    vel_y, vel_x = 1, 1

    # Scores
    score_left = 0
    score_right = 0

    while True:
        stdscr.clear()

        # Draw borders and center net
        stdscr.border()
        for y in range(1, sh - 1, 2):
            stdscr.addch(y, sw // 2, '|')

        # Display scoreboard and controls
        score_text = f" P1 (W/S): {score_left}   |   P2 (Up/Down): {score_right}   [Q to Quit] "
        stdscr.addstr(0, max(1, (sw - len(score_text)) // 2), score_text)

        # Draw paddles
        for i in range(paddle_h):
            stdscr.addch(left_y + i, 2, '█')
            stdscr.addch(right_y + i, sw - 3, '█')

        # Draw ball
        stdscr.addch(int(ball_y), int(ball_x), 'O')

        # Handle keyboard input
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            break
        elif key in (ord('w'), ord('W')) and left_y > 1:
            left_y -= 1
        elif key in (ord('s'), ord('S')) and left_y < sh - paddle_h - 1:
            left_y += 1
        elif key == curses.KEY_UP and right_y > 1:
            right_y -= 1
        elif key == curses.KEY_DOWN and right_y < sh - paddle_h - 1:
            right_y += 1

        # Move ball
        ball_y += vel_y
        ball_x += vel_x

        # Bounce off top and bottom walls
        if ball_y <= 1 or ball_y >= sh - 2:
            vel_y *= -1

        # Bounce off left paddle
        if ball_x == 3 and left_y <= ball_y < left_y + paddle_h:
            vel_x *= -1

        # Bounce off right paddle
        if ball_x == sw - 4 and right_y <= ball_y < right_y + paddle_h:
            vel_x *= -1

        # Check scoring conditions
        if ball_x <= 1:
            score_right += 1
            ball_y, ball_x = sh // 2, sw // 2
            vel_x = 1
            time.sleep(0.4)
        elif ball_x >= sw - 2:
            score_left += 1
            ball_y, ball_x = sh // 2, sw // 2
            vel_x = -1
            time.sleep(0.4)

        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
