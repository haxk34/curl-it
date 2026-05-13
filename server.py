from flask import Flask, Response
import time
import os

app = Flask(__name__)

# ---------- SETTINGS ----------
WIDTH = 50
HEIGHT = 12


# ---------- UTIL ----------
def clear():
    return "\033[2J\033[H"


def make_screen(player_y, obstacles):
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


def stream(frames, delay=0.06):
    def gen():
        for f in frames:
            yield clear() + f
            time.sleep(delay)
    return Response(gen(), mimetype="text/plain")


# =========================================================
# 🧪 PHYSICS DEMO
# =========================================================
@app.route("/physics")
def physics():

    y = 2
    vy = 0
    gravity = 0.35

    frames = []

    for _ in range(120):
        vy += gravity
        y += vy

        if y > HEIGHT - 2:
            y = HEIGHT - 2
            vy *= -0.6

        frames.append(make_screen(y, []))

    return stream(frames, 0.05)


# =========================================================
# 🎮 GEOMETRY DASH STYLE RUNNER
# =========================================================
@app.route("/gd")
def gd():

    y = HEIGHT - 2
    vy = 0
    gravity = 0.45
    jump_power = -3.8

    obstacles = [20, 35, 50, 70, 90]

    frames = []

    for t in range(160):

        # fake rhythm jump timing
        if t % 25 == 0:
            vy = jump_power

        # physics
        vy += gravity
        y += vy

        if y > HEIGHT - 2:
            y = HEIGHT - 2
            vy = 0

        # move obstacles left
        obstacles = [x - 1 for x in obstacles if x > 0]

        # spawn new obstacles
        if t % 30 == 0:
            obstacles.append(WIDTH - 1)

        frames.append(make_screen(y, obstacles))

    return stream(frames, 0.06)


# =========================================================
# 🏠 HOME
# =========================================================
@app.route("/")
def home():
    return """
Terminal Game Server

Routes:
/physics -> gravity demo
/gd      -> Geometry Dash style runner
"""


# =========================================================
# RUN (IMPORTANT FOR RENDER)
# =========================================================
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
