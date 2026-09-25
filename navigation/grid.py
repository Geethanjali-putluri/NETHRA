GRID_SIZE = 12

# 0 = free space
# 1 = obstacle

grid = [
    [0] * GRID_SIZE for _ in range(GRID_SIZE)
]

# Example obstacles
grid[4][4] = 1
grid[5][4] = 1
grid[6][4] = 1
grid[6][5] = 1
grid[6][6] = 1

START = (11, 0)
GOAL = (0, 11)


def print_grid(path=None):
    path = path or []

    for row in range(GRID_SIZE):
        line = ""

        for col in range(GRID_SIZE):
            position = (row, col)

            if position == START:
                line += "S "
            elif position == GOAL:
                line += "G "
            elif position in path:
                line += "* "
            elif grid[row][col] == 1:
                line += "X "
            else:
                line += ". "

        print(line)


print_grid()