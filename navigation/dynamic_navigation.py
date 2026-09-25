from grid import grid, START, GOAL, print_grid
from astar import a_star


def add_obstacle(row, col):
    if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
        grid[row][col] = 1
        print(f"🚧 Obstacle added at ({row}, {col})")


# Simulate a newly detected obstacle
add_obstacle(8, 5)

print("\nUpdated Grid:")
print_grid()

# Recalculate path
path = a_star(START, GOAL)

if path:
    print("\n🔄 New path found!")
    print("Path:", path)
    print("Path length:", len(path))

    print("\nNew Navigation Grid:")
    print_grid(path)
else:
    print("\n❌ No safe path available!")