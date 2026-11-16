#!/usr/bin/env python3
"""
Pong CLI — smooth, playable terminal Pong for Windows CMD / PowerShell.

Controls:
  W / S or ↑ / ↓  Move paddle
  Space            Pause / resume
  Enter            Start / restart
  Q / Esc          Quit

Run: py main.py
"""
import os
import sys
import time
import random
import shutil
import math

if os.name == "nt":
    import msvcrt
else:
    import tty
    import termios
    import select

# ANSI support in modern Windows terminals
if os.name == "nt":
    os.system("")

W, H = 72, 24
PADDLE_H = 5
FPS = 60
WIN_SCORE = 7
FRAME = 1 / FPS

# ANSI helpers
CSI = "\x1b["
def hide_cursor(): print(CSI + "?25l", end="", flush=True)
def show_cursor(): print(CSI + "?25h", end="", flush=True)
def clear(): print(CSI + "2J" + CSI + "H", end="", flush=True)
def move(x, y): return f"{CSI}{y};{x}H"
def paint(text, color): return f"{CSI}{color}m{text}{CSI}0m"

def read_keys():
    keys = []
    if os.name == "nt":
        while msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b"\\x00", b"\\xe0"):
                nxt = msvcrt.getch()
                keys.append({"H": "UP", "P": "DOWN"}.get(nxt.decode(errors="ignore"), ""))
            else:
                keys.append(ch.decode(errors="ignore").lower())
    else:
        while select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1)
            if ch == "\\x1b":
                seq = sys.stdin.read(2)
                keys.append({"[A": "UP", "[B": "DOWN"}.get(seq, ""))
            else:
                keys.append(ch.lower())
    return keys

class Pong:
    def __init__(self):
        self.reset_match()

    def reset_match(self):
        self.left_score = self.right_score = 0
        self.left_y = self.right_y = H / 2
        self.reset_ball(random.choice([-1, 1]))
        self.state = "menu"

    def reset_ball(self, direction):
        self.x, self.y = W / 2, H / 2
        self.speed = 27.0
        self.vx = direction * self.speed
        self.vy = random.choice([-1, 1]) * random.uniform(8, 13)

    def launch(self):
        self.reset_ball(random.choice([-1, 1]))
        self.state = "playing"

    def move_paddle(self, direction, dt):
        self.left_y += direction * 34 * dt
        self.left_y = max(PADDLE_H / 2, min(H - PADDLE_H / 2, self.left_y))

    def update(self, dt):
        if self.state != "playing":
            return
        # AI tracks ball, with reaction delay and a little imperfection.
        target = self.y + random.uniform(-1.0, 1.0)
        ai_center = self.right_y
        diff = target - ai_center
        ai_speed = 26
        self.right_y += max(-ai_speed * dt, min(ai_speed * dt, diff))
        self.right_y = max(PADDLE_H / 2, min(H - PADDLE_H / 2, self.right_y))

        # Substep movement prevents tunneling at higher speeds.
        steps = max(1, int(math.ceil(abs(self.vx * dt) / 0.45)))
        sx, sy = self.vx * dt / steps, self.vy * dt / steps
        for _ in range(steps):
            self.x += sx
            self.y += sy
            if self.y <= 1.5:
                self.y = 1.5
                self.vy = abs(self.vy)
            elif self.y >= H - 1.5:
                self.y = H - 1.5
                self.vy = -abs(self.vy)

            # Left paddle
            if self.vx < 0 and self.x <= 4.2 and self.x >= 2.8:
                if abs(self.y - self.left_y) <= PADDLE_H / 2 + 0.5:
                    self.x = 4.2
                    self.bounce(self.left_y, -1)
            # Right paddle
            if self.vx > 0 and self.x >= W - 4.2 and self.x <= W - 2.8:
                if abs(self.y - self.right_y) <= PADDLE_H / 2 + 0.5:
                    self.x = W - 4.2
                    self.bounce(self.right_y, 1)

        if self.x < 0:
            self.right_score += 1
            self.point(-1)
        elif self.x > W:
            self.left_score += 1
            self.point(1)

        if self.left_score >= WIN_SCORE or self.right_score >= WIN_SCORE:
            self.state = "over"

    def bounce(self, paddle_center, side):
        # Hit position controls angle; each return gets a little faster.
        offset = (self.y - paddle_center) / (PADDLE_H / 2)
        offset = max(-1.0, min(1.0, offset))
        self.speed = min(43, self.speed * 1.045 + 0.6)
        angle = offset * 0.95
        self.vx = side * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)

    def point(self, direction):
        self.state = "point"
        self.point_timer = time.monotonic() + 0.75
        self.next_direction = direction

    def draw(self):
        # Build complete frame in memory, then write once (no flicker).
        grid = [[" " for _ in range(W)] for _ in range(H)]
        # borders
        for x in range(W):
            grid[0][x] = "─"
            grid[H-1][x] = "─"
        for y in range(H):
            grid[y][0] = "│"
            grid[y][W-1] = "│"
        grid[0][0] = "┌"; grid[0][W-1] = "┐"
        grid[H-1][0] = "└"; grid[H-1][W-1] = "┘"
        for y in range(2, H-2):
            if y % 2 == 0: grid[y][W//2] = "┆"

        # paddles
        for yy in range(round(self.left_y - PADDLE_H/2), round(self.left_y + PADDLE_H/2)+1):
            if 1 <= yy < H-1: grid[yy][3] = "┃"
        for yy in range(round(self.right_y - PADDLE_H/2), round(self.right_y + PADDLE_H/2)+1):
            if 1 <= yy < H-1: grid[yy][W-4] = "┃"
        bx, by = int(round(self.x)), int(round(self.y))
        if 1 <= bx < W-1 and 1 <= by < H-1: grid[by][bx] = "●"

        out = [move(1,1), paint(f"  YOU  {self.left_score}     PONG     {self.right_score}  CPU  ", "1;97;44")]
        out.append(move(1,2))
        out.extend("".join(row) for row in grid)
        out.append(move(1,H+2))
        if self.state == "menu":
            out.append(paint("  ENTER to play   W/S or ↑/↓ to move   Q to quit", "96"))
        elif self.state == "paused":
            out.append(paint("  PAUSED — SPACE to resume", "93"))
        elif self.state == "point":
            out.append(paint("  POINT!  Get ready...", "92"))
        elif self.state == "over":
            winner = "YOU WIN!" if self.left_score > self.right_score else "CPU WINS!"
            out.append(paint(f"  {winner}  —  ENTER rematch / Q quit", "1;93"))
        else:
            out.append(paint("  W/S or ↑/↓ move    SPACE pause    Q quit    First to 7", "90"))
        print("".join(out), end="", flush=True)

    def run(self):
        old = None
        if os.name != "nt":
            old = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        hide_cursor()
        clear()
        self.draw()
        last = time.monotonic()
        try:
            while True:
                now = time.monotonic()
                dt = min(now - last, 0.04)
                last = now
                keys = read_keys()
                for k in keys:
                    if k in ("q", "\\x1b"):
                        return
                    if k in ("w", "UP"):
                        self.move_paddle(-1, dt if len(keys) == 1 else 0.04)
                    if k in ("s", "DOWN"):
                        self.move_paddle(1, dt if len(keys) == 1 else 0.04)
                    if k == " ":
                        if self.state == "playing": self.state = "paused"
                        elif self.state == "paused": self.state = "playing"
                    if k in ("\\r", "\\n"):
                        if self.state in ("menu", "point"): self.launch()
                        elif self.state == "over": self.reset_match()
                if self.state == "point" and now >= self.point_timer:
                    self.launch()
                self.update(dt)
                self.draw()
                time.sleep(max(0, FRAME - (time.monotonic() - now)))
        finally:
            show_cursor()
            clear()
            if old is not None:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)

if __name__ == "__main__":
    try:
        Pong().run()
    except KeyboardInterrupt:
        show_cursor()
        print("\\nExited.")
