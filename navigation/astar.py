from navigation.grid import grid, START, GOAL, print_grid
import heapq


def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(position):
    row, col = position

    directions = [
        (-1, 0),  # up
        (1, 0),   # down
        (0, -1),  # left
        (0, 1)    # right
    ]

    neighbors = []

    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc

        if 0 <= new_row < len(grid) and 0 <= new_col < len(grid[0]):
            if grid[new_row][new_col] == 0:
                neighbors.append((new_row, new_col))

    return neighbors


def a_star(start, goal):
    open_set = []

    heapq.heappush(open_set, (0, start))

    came_from = {}

    g_score = {start: 0}

    while open_set:

        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []

            while current in came_from:
                path.append(current)
                current = came_from[current]

            path.append(start)
            path.reverse()

            return path

        for neighbor in get_neighbors(current):

            new_cost = g_score[current] + 1

            if neighbor not in g_score or new_cost < g_score[neighbor]:

                came_from[neighbor] = current
                g_score[neighbor] = new_cost

                f_score = new_cost + heuristic(neighbor, goal)

                heapq.heappush(
                    open_set,
                    (f_score, neighbor)
                )

    return None


path = a_star(START, GOAL)

if path:
    print("✅ Path found!")
    print("Path:", path)
    print("Path length:", len(path))

    print("\nNavigation Grid:")
    print_grid(path)

else:
    print("❌ No path found.")