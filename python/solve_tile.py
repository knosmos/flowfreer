# carcassonne algorithm
import sys, os

mapping = {
    0: ("..", (0, 0, 0, 0)),  # up down left right
    1: ("──", (0, 0, 1, 1)),
    2: ("│ ", (1, 1, 0, 0)),
    3: ("┘ ", (1, 0, 1, 0)),
    4: ("└─", (1, 0, 0, 1)),
    5: ("┐ ", (0, 1, 1, 0)),
    6: ("┌─", (0, 1, 0, 1)),
    7: ("* ", (1, 1, 1, 1)),
}

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up  # down  # left  # right


def solve(puzzle, endpoints, ctr=0):
    print("===")
    print(ctr)
    render(puzzle)
    if ctr == len(puzzle) * len(puzzle[0]):
        return True

    i, j = divmod(ctr, len(puzzle[0]))
    for value in range(1, 7):
        puzzle[i][j] = value
        if is_valid(puzzle, endpoints, i, j, value):
            nxt_ctr = ctr + 1
            while (
                nxt_ctr < len(puzzle) * len(puzzle[0])
                and puzzle[nxt_ctr // len(puzzle[0])][nxt_ctr % len(puzzle[0])] != 0
            ):
                nxt_ctr += 1
            if solve(puzzle, endpoints, nxt_ctr):
                return True
        puzzle[i][j] = 0  # Backtrack

    return False  # No valid value found


def get_neighbors(puzzle, i, j, val):
    neighbors = []
    for idx, direction in enumerate(directions):
        ni, nj = i + direction[0], j + direction[1]
        if 0 <= ni < len(puzzle) and 0 <= nj < len(puzzle[0]):
            if mapping[val][1][idx]:
                neighbors.append((ni, nj))
    return neighbors


def is_valid(puzzle, endpoints, i, j, value):
    # connectivity checks
    for idx, direction in enumerate(directions):
        ni, nj = i + direction[0], j + direction[1]
        if 0 <= ni < len(puzzle) and 0 <= nj < len(puzzle[0]):
            if puzzle[ni][nj] in (0, 7):
                continue
            neighbor_neighbors = get_neighbors(puzzle, ni, nj, puzzle[ni][nj])
            if mapping[value][1][idx] != ((i, j) in neighbor_neighbors):
                return False
        elif mapping[value][1][idx] == 1:
            return False
    # pathing checks
    for s, e, c in endpoints:
        src, dest = None, None
        for ni, nj in [s, e]:
            links = [
                n
                for n in get_neighbors(puzzle, ni, nj, 7)
                if puzzle[n[0]][n[1]] != 0
                and (puzzle[n[0]][n[1]] != 7 or n == s or n == e)
                and (ni, nj) in get_neighbors(puzzle, n[0], n[1], puzzle[n[0]][n[1]])
            ]
            zeroes = [
                n for n in get_neighbors(puzzle, ni, nj, 7) if puzzle[n[0]][n[1]] == 0
            ]
            if len(links) > 1:
                return False
            if len(zeroes) == 0 and len(links) != 1:
                return False
        stack = [s]
        visited = {s}
        while stack:
            current = stack.pop()
            if current == e:
                break
            for n in get_neighbors(
                puzzle, current[0], current[1], puzzle[current[0]][current[1]]
            ):
                if (
                    n not in visited
                    and (current[0], current[1])
                    in get_neighbors(puzzle, n[0], n[1], puzzle[n[0]][n[1]])
                    and (puzzle[current[0]][current[1]] != 7 or puzzle[n[0]][n[1]] != 7)
                ):
                    stack.append(n)
                    visited.add(n)
                    if puzzle[n[0]][n[1]] == 7 and n != e:
                        return False
        stack = [e]
        visited = {e}
        while stack:
            current = stack.pop()
            if current == s:
                break
            for n in get_neighbors(
                puzzle, current[0], current[1], puzzle[current[0]][current[1]]
            ):
                if (
                    n not in visited
                    and (current[0], current[1])
                    in get_neighbors(puzzle, n[0], n[1], puzzle[n[0]][n[1]])
                    and (puzzle[current[0]][current[1]] != 7 or puzzle[n[0]][n[1]] != 7)
                ):
                    stack.append(n)
                    visited.add(n)
                    if puzzle[n[0]][n[1]] == 7 and n != s:
                        return False
    # efficiency check
    colors = color_map(puzzle, endpoints)
    # all neighbors not linked must be different colors
    for idx, direction in enumerate(directions):
        ni, nj = i + direction[0], j + direction[1]
        if 0 <= ni < len(puzzle) and 0 <= nj < len(puzzle[0]):
            if not mapping[puzzle[i][j]][1][idx]:
                if (
                    colors[i][j] == colors[ni][nj]
                    and colors[i][j] != -1
                    and colors[ni][nj] != -1
                ):
                    print(f"Efficiency check failed at ({i}, {j}) and ({ni}, {nj})")
                    return False
    return True


def color_map(puzzle, endpoints):
    # floodfill to find color of each square
    colors = [[-1] * len(puzzle[0]) for _ in range(len(puzzle))]
    for s, e, c in endpoints:
        stack = [s]
        visited = {s}
        while stack:
            current = stack.pop()
            colors[current[0]][current[1]] = c
            for n in get_neighbors(
                puzzle, current[0], current[1], puzzle[current[0]][current[1]]
            ):
                if n not in visited and (current[0], current[1]) in get_neighbors(
                    puzzle, n[0], n[1], puzzle[n[0]][n[1]]
                ):
                    stack.append(n)
                    visited.add(n)
    return colors


def build(endpoints, n, m):
    puzzle = [[0] * m for _ in range(n)]
    for s, e, c in endpoints:
        puzzle[s[0]][s[1]] = 7
        puzzle[e[0]][e[1]] = 7
    return puzzle


def render(puzzle):
    global ctr
    sys.stdout.write("\033[H")
    print("✧˖° FLOW FREER ✧˖°")
    print(f"step = {ctr}")
    print()
    for row in puzzle:
        print("".join(mapping[cell][0] for cell in row))
    print()
    ctr += 1


ctr = 0

# print(solve([[0, 0, 0], [0, 0, 0], [0, 0, 0], [0,0,0]], []))
endpoints = [
    [(4, 4), (5, 7), 0],
    [(5, 2), (6, 7), 1],
    [(6, 3), (1, 6), 2],
    [(4, 2), (6, 6), 3],
]
# endpoints = [
#     [(0, 0), (4, 1), 0],
#     [(0, 2), (3, 1), 1],
#     [(0, 4), (3, 3), 2],
#     [(1, 2), (4, 2), 3],
#     [(1, 4), (4, 3), 4]
# ]
# endpoints = [
#     [(0, 0), (1, 1), 0]
# ]


def read_input(fname):
    board = open(fname, "r").read().split("\n")
    endpoints_dict = {}
    n = len(board)
    m = len(board[0])
    for i in range(n):
        for j in range(m):
            if board[i][j] == ".":
                continue
            if board[i][j] not in endpoints_dict:
                endpoints_dict[board[i][j]] = []
            endpoints_dict[board[i][j]].append((i, j))
    endpoints = []
    for color, coords in endpoints_dict.items():
        if len(coords) != 2:
            raise ValueError(f"Invalid input: {color} has {len(coords)} endpoints")
        endpoints.append((coords[0], coords[1], int(color)))
    return endpoints, n, m


puzzle = build(endpoints, 8, 8)
start = 0

endpoints, n, m = read_input("test_inputs/input3.txt")
puzzle = build(endpoints, n, m)

os.system("cls" if os.name == "nt" else "clear")
while (
    start < len(puzzle) * len(puzzle[0])
    and puzzle[start // len(puzzle[0])][start % len(puzzle[0])] != 0
):
    start += 1
print(solve(puzzle, endpoints, start))
