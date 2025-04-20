'''
attack plan:
backtracking approach
- move only the most constrained color
- instacomplete if only one path left
- kill if:
    - any color has no paths left
'''

import os, sys

mapping = { # mod 7
    0: "v",
    1: "^",
    2: ">",
    3: "<",
    4: "*",
    5: ".",
    6: "#"
}

ANSI_START = "\x1b[1;"
ANSI_END = "\x1b[0m"
colors = [41, 42, 43, 44, 45, 46, 47] # red, green, yellow, blue, magenta, cyan, white

def solve(puzzle, endpoints):
    # find most constrained color
    # rfn through all possible moves
    render(puzzle)
    # test solvability for remaining colors
    if not dfs_test(puzzle, endpoints):
        print("partition check failed")
        return
    # test fillability of remaining squares
    if not empty_test(puzzle, endpoints):
        print("empty test failed")
        return

    # make next move
    start, end, color = endpoints[0]
    nxts = [
        (start[0] + 1, start[1]), # down
        (start[0] - 1, start[1]), # up
        (start[0], start[1] + 1), # right
        (start[0], start[1] - 1), # left
    ]
    for i, nxt in enumerate(nxts):
        if nxt[0] < 0 or nxt[0] >= len(puzzle) or nxt[1] < 0 or nxt[1] >= len(puzzle[0]):
            continue
        if puzzle[nxt[0]][nxt[1]] != 5 and nxt != end:
            continue
        new_cell_neighbors = [
            (nxt[0] + 1, nxt[1]), # down
            (nxt[0] - 1, nxt[1]), # up
            (nxt[0], nxt[1] + 1), # right
            (nxt[0], nxt[1] - 1), # left
        ]
        for neighbor in new_cell_neighbors:
            if neighbor == start or neighbor == end:
                continue
            if neighbor[0] < 0 or neighbor[0] >= len(puzzle) or neighbor[1] < 0 or neighbor[1] >= len(puzzle[0]):
                continue
            if puzzle[neighbor[0]][neighbor[1]] // len(mapping) == color and puzzle[neighbor[0]][neighbor[1]] != 5:
                break
        else:
            original_endpoint_flag = puzzle[start[0]][start[1]] % len(mapping) == 4
            if not original_endpoint_flag:
                puzzle[start[0]][start[1]] = color * len(mapping) + i
            if nxt == end:
                # move to next color
                print("found end", nxt, end, color)
                new_endpoints = endpoints[1:]
                if len(new_endpoints) == 0:
                    print("solved")
                    render(puzzle)
                    sys.exit(0)
                solve(puzzle, new_endpoints)
            else:
                endpoints[0] = (nxt, end, color)
                solve(puzzle, endpoints)
                endpoints[0] = (start, end, color)
            if not original_endpoint_flag:
                puzzle[start[0]][start[1]] = 5

def dfs_test(puzzle, endpoints):
    for start, end, color in endpoints:
        stack = [start]
        visited = set()
        while stack:
            curr = stack.pop()
            if curr == end:
                break
            visited.add(curr)
            # check all possible moves
            nxts = [
                (curr[0] + 1, curr[1]), # down
                (curr[0] - 1, curr[1]), # up
                (curr[0], curr[1] + 1), # right
                (curr[0], curr[1] - 1), # left
            ]
            for nxt in nxts:
                if nxt[0] < 0 or nxt[0] >= len(puzzle) or nxt[1] < 0 or nxt[1] >= len(puzzle[0]):
                    continue
                if puzzle[nxt[0]][nxt[1]] != 5 and nxt != end:
                    continue
                if nxt not in visited:
                    stack.append(nxt)
        else:
            return False
    return True

def empty_test(puzzle, endpoints):
    stack = []
    for start, end, color in endpoints:
        stack.append(start)
        stack.append(end)
    visited = set()
    while stack:
        curr = stack.pop()
        if curr in visited:
            continue
        visited.add(curr)
        # check all possible moves
        nxts = [
            (curr[0] + 1, curr[1]), # down
            (curr[0] - 1, curr[1]), # up
            (curr[0], curr[1] + 1), # right
            (curr[0], curr[1] - 1), # left
        ]
        for nxt in nxts:
            if nxt[0] < 0 or nxt[0] >= len(puzzle) or nxt[1] < 0 or nxt[1] >= len(puzzle[0]):
                continue
            if puzzle[nxt[0]][nxt[1]] != 5 and nxt not in endpoints:
                continue
            stack.append(nxt)
    for i, row in enumerate(puzzle):
        for j, cell in enumerate(row):
            if cell == 5:
                if (i, j) not in visited:
                    return False
    return True

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def render(puzzle):
    global ctr
    sys.stdout.write("\033[H")
    print("✧˖° FLOW FREER ✧˖°")
    print(f"step = {ctr}")
    print()
    for row in puzzle:
        print("".join([
            f"{ANSI_START}{colors[i // 7]}m{mapping[i % 7]} {ANSI_END}"
            if i != 5 else ". "
            for i in row
        ]))
    print()
    ctr += 1

def build(endpoints, n, m):
    puzzle = [[5 for _ in range(m)] for _ in range(n)]
    for start, end, color in endpoints:
        puzzle[start[0]][start[1]] = color * len(mapping) + 4
        puzzle[end[0]][end[1]] = color * len(mapping) + 4
    return puzzle

def read_input():
    board = open("input.txt", "r").read().split("\n")
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


#endpoints = [((0, 0), (1, 1), 0), ((0, 1), (2, 0), 1)]
# endpoints = [
#     [(0, 0), (4, 1), 0],
#     [(0, 2), (3, 1), 1],
#     [(0, 4), (3, 3), 2],
#     [(1, 2), (4, 2), 3],
#     [(1, 4), (4, 3), 4]
# ]

ctr = 0

# endpoints = [
#     [(4,4),(5,7),0],
#     [(5,2),(6,7),1],
#     [(6,3),(1,6),2],
#     [(4,2),(6,6),3],
# ]

#puzzle = build(endpoints, 8, 8)
endpoints, n, m = read_input()
puzzle = build(endpoints, n, m)

clear()
render(puzzle)
solve(puzzle, endpoints)