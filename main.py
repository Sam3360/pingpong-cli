
import os
import time
import random

WIDTH = 30
WIN_SCORE = 5

p1_score = 0
p2_score = 0

print("🏓 PINGPONG CLI")
print("Player 1: A | Player 2: D")
print("Press ENTER to start!")
input()

while p1_score < WIN_SCORE and p2_score < WIN_SCORE:
    ball = random.choice(["LEFT", "RIGHT"])

    print("\n" + "=" * WIDTH)
    print(f"Player 1: {p1_score} | Player 2: {p2_score}")
    print(f"Ball approaching: {ball}")
    print("=" * WIDTH)

    hit = input("Hit the ball? (y/n): ").lower()

    if hit == "y":
        if random.random() > 0.2:
            print("Nice hit!")
            time.sleep(0.5)

            if random.random() > 0.5:
                p1_score += 1
                print("Point for Player 1!")
            else:
                p2_score += 1
                print("Point for Player 2!")
        else:
            print("Missed!")
            p2_score += 1
    else:
        print("Missed!")
        p2_score += 1

    time.sleep(0.5)

print("\n" + "=" * WIDTH)
print("🏆 GAME OVER")

if p1_score > p2_score:
    print("PLAYER 1 WINS!")
else:
    print("PLAYER 2 WINS!")

print(f"Final Score: {p1_score} - {p2_score}")
