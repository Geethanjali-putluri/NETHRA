import sys
import os
import time

# Add project root to Python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from navigation.grid import grid, START, GOAL
from navigation.astar import a_star


def get_direction(current, next_position):
    current_row, current_col = current
    next_row, next_col = next_position

    if next_row < current_row:
        return "UP"
    elif next_row > current_row:
        return "DOWN"
    elif next_col < current_col:
        return "LEFT"
    elif next_col > current_col:
        return "RIGHT"


# Find path
path = a_star(START, GOAL)

if not path:
    print("❌ No path available.")
    exit()

print("🚗 NETHRA Rover Simulation Started")
print("-----------------------------------")

current_position = START

for next_position in path[1:]:

    direction = get_direction(current_position, next_position)

    print(
        f"Rover: {current_position} "
        f"→ {direction} → {next_position}"
    )

    current_position = next_position

    time.sleep(0.3)

print("-----------------------------------")
print("🎯 Destination reached!")
print(f"Final position: {current_position}")