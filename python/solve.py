"""
attack plan:
backtracking approach
- move only the most constrained color
- instacomplete if only one path left
- kill if:
    - any color has no paths left
"""

import os, sys, time
from collections import deque

mapping = {0: "v", 1: "^", 2: ">", 3: "<", 4: "*", 5: ".", 6: "#"}  # mod 7

ANSI_START = "\x1b[1;"
ANSI_END = "\x1b[0m"
colors = [
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
]  # red, green, yellow, blue, magenta, cyan, white


def solve(puzzle, endpoints, prev=-1):
    # find most constrained color
    # most_constrained = -1
    # most_constrained_count = float("inf")
    # for i, (start, end, color) in enumerate(endpoints):
    #     if start == end:
    #         continue
    #     neighbors = get_neighbors(start)
    #     open_squares = 0
    #     for neighbor in neighbors:
    #         if neighbor[0] < 0 or neighbor[0] >= len(puzzle) or neighbor[1] < 0 or neighbor[1] >= len(puzzle[0]):
    #             continue
    #         if puzzle[neighbor[0]][neighbor[1]] == 5:
    #             open_squares += 1
    #     if open_squares < most_constrained_count:
    #         most_constrained_count = open_squares
    #         most_constrained = i
    # if most_constrained == -1:
    #     print("solved")
    #     render(puzzle)
    #     sys.exit(0)
    most_constrained = 0
    while (
        most_constrained < len(endpoints)
        and endpoints[most_constrained][0] == endpoints[most_constrained][1]
    ):
        most_constrained += 1
    if most_constrained == len(endpoints):
        print("solved")
        render(puzzle)
        sys.exit(0)

    # rfn through all possible moves
    # time.sleep(0.5)
    render(puzzle)
    print("most constrained", most_constrained, endpoints[most_constrained])
    # test solvability for remaining colors
    if not dfs_test(puzzle, endpoints):
        print("partition check failed             ")
        return
    # test fillability of remaining squares
    if not empty_test3(puzzle, endpoints):
        print("empty test failed                  ")
        return

    # make next move
    start, end, color = endpoints[most_constrained]
    nxts = get_neighbors(start)
    nxts_indexed = [(i, nxt) for i, nxt in enumerate(nxts)]

    # reorder search order heuristically
    nxts_indexed.sort(
        key=lambda x: (
            float("-inf") if x[0] == prev else -(x[1][0] - end[0] + x[1][1] - end[1])
        )
    )
    for i in range(4):
        if nxts_indexed[i][1] == end:
            nxts_indexed = [(nxts_indexed[i][0], end)]
            break

    for i, nxt in nxts_indexed:
        if (
            nxt[0] < 0
            or nxt[0] >= len(puzzle)
            or nxt[1] < 0
            or nxt[1] >= len(puzzle[0])
        ):
            continue
        if puzzle[nxt[0]][nxt[1]] != 5 and nxt != end:
            continue
        for s, e, _ in endpoints:
            if s == nxt or e == nxt and (s != start or e != end):
                break
        else:
            new_cell_neighbors = get_neighbors(nxt)
            for neighbor in new_cell_neighbors:
                if neighbor == start or neighbor == end:
                    continue
                if (
                    neighbor[0] < 0
                    or neighbor[0] >= len(puzzle)
                    or neighbor[1] < 0
                    or neighbor[1] >= len(puzzle[0])
                ):
                    continue
                if (
                    puzzle[neighbor[0]][neighbor[1]] // len(mapping) == color
                    and puzzle[neighbor[0]][neighbor[1]] != 5
                ):
                    break
            else:
                original_endpoint_flag = puzzle[start[0]][start[1]] % len(mapping) == 4
                if not original_endpoint_flag:
                    puzzle[start[0]][start[1]] = color * len(mapping) + i
                if puzzle[nxt[0]][nxt[1]] == 5:
                    puzzle[nxt[0]][nxt[1]] = color * len(mapping) + i
                endpoints[most_constrained] = (nxt, end, color)
                solve(puzzle, endpoints, i)
                endpoints[most_constrained] = (start, end, color)
                if not original_endpoint_flag:
                    puzzle[start[0]][start[1]] = 5
                if puzzle[nxt[0]][nxt[1]] == color * len(mapping) + i:
                    puzzle[nxt[0]][nxt[1]] = 5


def get_neighbors(cell):
    return [
        (cell[0] + 1, cell[1]),  # down
        (cell[0] - 1, cell[1]),  # up
        (cell[0], cell[1] + 1),  # right
        (cell[0], cell[1] - 1),  # left
    ]


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
            nxts = get_neighbors(curr)
            for nxt in nxts:
                if (
                    nxt[0] < 0
                    or nxt[0] >= len(puzzle)
                    or nxt[1] < 0
                    or nxt[1] >= len(puzzle[0])
                ):
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
        nxts = get_neighbors(curr)
        for nxt in nxts:
            if (
                nxt[0] < 0
                or nxt[0] >= len(puzzle)
                or nxt[1] < 0
                or nxt[1] >= len(puzzle[0])
            ):
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


def empty_test2(puzzle, endpoints):
    # test if every empty cell is reachable from two of the same
    # colored endpoints
    viable = set()
    for start, end, color in endpoints:
        stack = [start]
        visited = set()
        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            # check all possible moves
            nxts = get_neighbors(curr)
            for nxt in nxts:
                if (
                    nxt[0] < 0
                    or nxt[0] >= len(puzzle)
                    or nxt[1] < 0
                    or nxt[1] >= len(puzzle[0])
                ):
                    continue
                if puzzle[nxt[0]][nxt[1]] != 5:
                    continue
                stack.append(nxt)
        stack = [end]
        visited2 = set()
        while stack:
            curr = stack.pop()
            if curr in visited2:
                continue
            visited2.add(curr)
            # check all possible moves
            nxts = get_neighbors(curr)
            for nxt in nxts:
                if (
                    nxt[0] < 0
                    or nxt[0] >= len(puzzle)
                    or nxt[1] < 0
                    or nxt[1] >= len(puzzle[0])
                ):
                    continue
                if puzzle[nxt[0]][nxt[1]] != 5:
                    continue
                stack.append(nxt)
        intersection = visited.intersection(visited2)
        viable.update(intersection)
    for i, row in enumerate(puzzle):
        for j, cell in enumerate(row):
            if cell == 5:
                if (i, j) not in viable:
                    return False
    return True


def empty_test3(puzzle, endpoints):
    # test if every empty cell is reachable from two of the same
    # colored endpoints
    viable = set()
    for start, end, color in endpoints:
        stack = [start]
        visited = set()
        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            # check all possible moves
            nxts = get_neighbors(curr)
            for nxt in nxts:
                if (
                    nxt[0] < 0
                    or nxt[0] >= len(puzzle)
                    or nxt[1] < 0
                    or nxt[1] >= len(puzzle[0])
                ):
                    continue
                if puzzle[nxt[0]][nxt[1]] != 5:
                    continue
                stack.append(nxt)
        stack = [end]
        visited2 = set()
        while stack:
            curr = stack.pop()
            if curr in visited2:
                continue
            visited2.add(curr)
            # check all possible moves
            nxts = get_neighbors(curr)
            for nxt in nxts:
                if (
                    nxt[0] < 0
                    or nxt[0] >= len(puzzle)
                    or nxt[1] < 0
                    or nxt[1] >= len(puzzle[0])
                ):
                    continue
                if puzzle[nxt[0]][nxt[1]] != 5:
                    continue
                stack.append(nxt)
        intersection = visited.intersection(visited2)
        viable.update(intersection)
    endpoints_set = set()
    for start, end, color in endpoints:
        endpoints_set.add(start)
        endpoints_set.add(end)
    for i, row in enumerate(puzzle):
        for j, cell in enumerate(row):
            if cell == 5:
                if (i, j) not in viable:
                    return False
                neighbors = get_neighbors((i, j))
                num_empty = 0
                for neighbor in neighbors:
                    if (
                        neighbor[0] < 0
                        or neighbor[0] >= len(puzzle)
                        or neighbor[1] < 0
                        or neighbor[1] >= len(puzzle[0])
                    ):
                        continue
                    if (
                        puzzle[neighbor[0]][neighbor[1]] == 5
                        or neighbor in endpoints_set
                    ):
                        num_empty += 1
                if num_empty < 2:
                    return False
    return True


def clear():
    os.system("cls" if os.name == "nt" else "clear")


ctr = 0


def render(puzzle):
    # clear()
    global ctr
    sys.stdout.write("\033[H")
    print("✧˖° FLOW FREER ✧˖°")
    print(f"step = {ctr}")
    print()
    for row in puzzle:
        print(
            "".join(
                [
                    (
                        f"{ANSI_START}{colors[i // 7]}m{mapping[i % 7]} {ANSI_END}"
                        if i != 5
                        else ". "
                    )
                    for i in row
                ]
            )
        )
    print()
    ctr += 1


def build(endpoints, n, m):
    puzzle = [[5 for _ in range(m)] for _ in range(n)]
    for start, end, color in endpoints:
        puzzle[start[0]][start[1]] = color * len(mapping) + 4
        puzzle[end[0]][end[1]] = color * len(mapping) + 4
    return puzzle


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


if __name__ == "__main__":
    # endpoints = [((0, 0), (1, 1), 0), ((0, 1), (2, 0), 1)]
    # endpoints = [
    #     [(0, 0), (4, 1), 0],
    #     [(0, 2), (3, 1), 1],
    #     [(0, 4), (3, 3), 2],
    #     [(1, 2), (4, 2), 3],
    #     [(1, 4), (4, 3), 4]
    # ]
    endpoints = [
        [(4, 4), (5, 7), 0],
        [(5, 2), (6, 7), 1],
        [(6, 3), (1, 6), 2],
        [(4, 2), (6, 6), 3],
    ]

    puzzle = build(endpoints, 8, 8)
    endpoints, n, m = read_input("test_inputs/input.txt")
    puzzle = build(endpoints, n, m)

    clear()
    render(puzzle)
    solve(puzzle, endpoints)
