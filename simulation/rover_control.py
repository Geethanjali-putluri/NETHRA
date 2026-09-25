import tkinter as tk
import sys
import os

# Project root
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from navigation.grid import grid, START, GOAL
from navigation.astar import a_star


# -----------------------------
# SETTINGS
# -----------------------------

GRID_SIZE = len(grid)
CELL_SIZE = 50

rover_position = list(START)
running = False
adding_obstacle = False


# -----------------------------
# WINDOW
# -----------------------------

root = tk.Tk()
root.title("NETHRA - Autonomous Rover")
root.geometry("700x800")
root.resizable(False, False)


# -----------------------------
# TITLE
# -----------------------------

title = tk.Label(
    root,
    text="NETHRA — Autonomous Search & Rescue Rover",
    font=("Arial", 18, "bold")
)

title.pack(pady=10)


# -----------------------------
# CONTROL BUTTONS
# -----------------------------

control_frame = tk.Frame(root)
control_frame.pack(pady=10)


def start_rover():
    global running

    if not running:
        running = True
        status_label.config(text="STATUS: NAVIGATING")
        move_rover()


def stop_rover():
    global running

    running = False
    status_label.config(text="STATUS: STOPPED")


def add_obstacle_mode():
    global adding_obstacle

    adding_obstacle = True

    status_label.config(
        text="STATUS: Click a grid cell to add obstacle"
    )


start_button = tk.Button(
    control_frame,
    text="START",
    width=15,
    height=2,
    command=start_rover
)

start_button.grid(row=0, column=0, padx=8)


stop_button = tk.Button(
    control_frame,
    text="STOP",
    width=15,
    height=2,
    command=stop_rover
)

stop_button.grid(row=0, column=1, padx=8)


obstacle_button = tk.Button(
    control_frame,
    text="ADD OBSTACLE",
    width=15,
    height=2,
    command=add_obstacle_mode
)

obstacle_button.grid(row=0, column=2, padx=8)


# -----------------------------
# STATUS
# -----------------------------

status_label = tk.Label(
    root,
    text="STATUS: READY",
    font=("Arial", 12, "bold")
)

status_label.pack(pady=8)


# -----------------------------
# GRID CANVAS
# -----------------------------

canvas = tk.Canvas(
    root,
    width=GRID_SIZE * CELL_SIZE,
    height=GRID_SIZE * CELL_SIZE,
    bg="white"
)

canvas.pack(pady=15)


# -----------------------------
# DRAW GRID
# -----------------------------

def draw_grid():

    canvas.delete("all")

    path = a_star(
        tuple(rover_position),
        GOAL
    )

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            fill = "white"

            # Obstacle
            if grid[row][col] == 1:
                fill = "black"

            # Path
            if path and (row, col) in path:
                fill = "lightblue"

            # Goal
            if (row, col) == GOAL:
                fill = "gold"

            # Rover
            if (row, col) == tuple(rover_position):
                fill = "red"

            canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=fill,
                outline="gray"
            )

            # Coordinates
            canvas.create_text(
                x1 + 8,
                y1 + 8,
                text=f"{row},{col}",
                anchor="nw",
                font=("Arial", 7)
            )

    # Rover label

    row, col = rover_position

    canvas.create_text(
        col * CELL_SIZE + CELL_SIZE / 2,
        row * CELL_SIZE + CELL_SIZE / 2,
        text="R",
        fill="white",
        font=("Arial", 18, "bold")
    )

    # Goal label

    row, col = GOAL

    canvas.create_text(
        col * CELL_SIZE + CELL_SIZE / 2,
        row * CELL_SIZE + CELL_SIZE / 2,
        text="G",
        font=("Arial", 18, "bold")
    )


# -----------------------------
# ROVER MOVEMENT
# -----------------------------

def move_rover():

    global running

    if not running:
        return

    current = tuple(rover_position)

    if current == GOAL:

        running = False

        status_label.config(
            text="STATUS: MISSION COMPLETE"
        )

        return

    path = a_star(
        current,
        GOAL
    )

    if not path:

        running = False

        status_label.config(
            text="STATUS: NO SAFE PATH"
        )

        return

    # Move to next cell

    if len(path) > 1:

        next_position = path[1]

        rover_position[0] = next_position[0]
        rover_position[1] = next_position[1]

    draw_grid()

    root.after(
        500,
        move_rover
    )


# -----------------------------
# ADD OBSTACLE BY CLICKING
# -----------------------------

def grid_click(event):

    global adding_obstacle

    if not adding_obstacle:
        return

    col = event.x // CELL_SIZE
    row = event.y // CELL_SIZE

    # Don't place obstacle on rover
    if (row, col) == tuple(rover_position):
        return

    # Don't place obstacle on goal
    if (row, col) == GOAL:
        return

    grid[row][col] = 1

    adding_obstacle = False

    status_label.config(
        text=f"STATUS: Obstacle added at ({row},{col})"
    )

    draw_grid()


canvas.bind(
    "<Button-1>",
    grid_click
)


# -----------------------------
# INITIAL DISPLAY
# -----------------------------

draw_grid()

root.mainloop()