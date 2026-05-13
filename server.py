from flask import Flask, Response
import time
import os

app = Flask(__name__)

# ---------- SCREEN SETTINGS ----------
WIDTH = 50
HEIGHT = 12

# ---------- UTIL ----------
def clear():
    return "\033[2J\033[H"

def make_grid(player_y, obstacles):
    grid = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # ground
    for x in range(WIDTH):
        grid[HEIGHT - 1][x] = "_"

    # player
    py = int(player_y)
    px = 5
    if 0 <= py < HEIGHT:
        grid[py][px] = "O"

    # obstacles
    for ox in obstacles:
        if 0 <= ox < WIDTH:
            grid[HEIGHT - 2][ox] = "#"

    return "\n".join("".join(row) for row in grid)

def stream(frames, delay=0.08):
    def gen():
        for f in frames:
            yield clear() + f
            time.sleep(delay)
    return Response(gen(), mimetype="text/plain")

# ---------- TEST PHYSICS ----------
@app.route("/physics")
def test():

    y = 2
    vy = 0
    gravity = 0.4

    frames = []

    for _ in range(100):

        vy += gravity
        y += vy

        if y > HEIGHT - 2:
            y = HEIGHT - 2
            vy *= -0.7

        frames.append(make_grid(y, []))

    return stream(frames, 0.05)

# ---------- GD RUNNER ----------
@app.route("/gd")
def gd():

    y = HEIGHT - 2
    vy = 0
    gravity = 0.5
    jump = -3.5

    obstacles = [20, 40, 60, 80, 100]

    frames = []

    for t in range(120):

        # auto jump rhythm
        if t % 20 == 0:
            vy = jump

        vy += gravity
        y += vy

        if y > HEIGHT - 2:
            y = HEIGHT - 2
            vy = 0

        # move obstacles
        obstacles = [x - 1 for x in obstacles if x > 0]

        # spawn new obstacles
        if t % 25 == 0:
            obstacles.append(WIDTH - 1)

        frames.append(make_grid(y, obstacles))

    return stream(frames, 0.06)

# ---------- HOME ----------
@app.route("/")
def home():
    return """
Terminal GD Demo

curl /physics -> physics
curl /gd   -> geometry dash runner
"""

# ---------- RUN ----------
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)