import pycosat

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
]

def render(puzzle):
    global ctr
    print("✧˖° FLOW FREER ✧˖°")
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

def solve(endpoints, n, m):
    clauses = []
    num_colors = len(endpoints)
    # encoding: cell (i, j) with color k is represented by (i * m + j) * num_colors + k + 1
    def encode(i, j, k):
        return (i * m + j) * num_colors + k + 1

    def decode(x):
        x -= 1
        k = x % num_colors
        x //= num_colors
        j = x % m
        i = x // m
        return (i, j, k)

    # neighbors
    def get_neighbors(i, j):
        neighbors = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < m:
                neighbors.append((ni, nj))
        return neighbors

    endpoint_mapping = {}
    for s, e, c in endpoints:
        endpoint_mapping[(s[0], s[1])] = c
        endpoint_mapping[(e[0], e[1])] = c
    # each cell has exactly one color
    # endpoint cells have their designated color
    # print("endpoint_mapping", endpoint_mapping)
    # print("SETTING CELL COLORS")
    for i in range(n):
        for j in range(m):
            # print("i,j", i, j)
            if (i, j) in endpoint_mapping:
                c = endpoint_mapping[(i, j)]
                # print("endpoint", i, j, c)
                clauses.append([encode(i, j, c)])
                # print([encode(i, j, c)])
                for k in range(num_colors):
                    if k != c:
                        clauses.append([-encode(i, j, k)])
                        # print([-encode(i, j, k)])
            else:
                clauses.append([encode(i, j, k) for k in range(num_colors)])
                # print([encode(i, j, k) for k in range(num_colors)])
                for k in range(num_colors):
                    for k2 in range(k + 1, num_colors):
                        clauses.append([-encode(i, j, k), -encode(i, j, k2)])
                        # print([-encode(i, j, k), -encode(i, j, k2)])
    # connecting cells have exactly two neighbors with the same color
    # endpoint cells have exactly one neighbor with the same color
    # print("CONNECTING CELLS")
    for i in range(n):
        for j in range(m):
            # print("i,j", i, j)
            neighbors = get_neighbors(i, j)
            if (i, j) in endpoint_mapping:
                # endpoint cell
                c = endpoint_mapping[(i, j)]
                clauses.append([encode(n1, n2, c) for n1, n2 in neighbors])
                # print([encode(n1, n2, c) for n1, n2 in neighbors])
                for n1 in range(len(neighbors)):
                    for n2 in range(n1 + 1, len(neighbors)):
                        ni1, nj1 = neighbors[n1]
                        ni2, nj2 = neighbors[n2]
                        clauses.append([-encode(ni1, nj1, c), -encode(ni2, nj2, c)])
                        # print([-encode(ni1, nj1, c), -encode(ni2, nj2, c)])
            else:
                # normal cell
                for k in range(num_colors):
                    # this encodes the condition that exactly two neighbors have color k (if (i, j) has color k)
                    if len(neighbors) == 2:
                        clauses.append([-encode(i, j, k), encode(neighbors[0][0], neighbors[0][1], k)])
                        clauses.append([-encode(i, j, k), encode(neighbors[1][0], neighbors[1][1], k)])
                    # in any group of two neighbors, at least one has color k
                    # and at least one of the three neighbors does not has color k
                    if len(neighbors) == 3:
                        for n1 in range(len(neighbors)):
                            for n2 in range(n1 + 1, len(neighbors)):
                                ni1, nj1 = neighbors[n1]
                                ni2, nj2 = neighbors[n2]
                                clauses.append([-encode(i, j, k), encode(ni1, nj1, k), encode(ni2, nj2, k)])
                        clauses.append([-encode(i, j, k)] + [-encode(ni, nj, k) for ni, nj in neighbors])
                    # in every group of three neighbors, at least one does not have color k
                    # and at least one has color k
                    if len(neighbors) == 4:
                        for n1 in range(len(neighbors)):
                            for n2 in range(n1 + 1, len(neighbors)):
                                for n3 in range(n2 + 1, len(neighbors)):
                                    ni1, nj1 = neighbors[n1]
                                    ni2, nj2 = neighbors[n2]
                                    ni3, nj3 = neighbors[n3]
                                    clauses.append([-encode(i, j, k), -encode(ni1, nj1, k), -encode(ni2, nj2, k), -encode(ni3, nj3, k)])
                                    clauses.append([-encode(i, j, k), encode(ni1, nj1, k), encode(ni2, nj2, k), encode(ni3, nj3, k)])
    print(len(clauses), "clauses")
    sol_raw = pycosat.solve(clauses)
    # print("sol_raw", sol_raw)
    color_board = [[0] * m for _ in range(n)]
    for x in sol_raw:
        if x > 0:
            i, j, k = decode(x)
            color_board[i][j] = k
    
    # convert to puzzle format used in original solver
    puzzle = [[0] * m for _ in range(n)]
    for s, e, c in endpoints:
        puzzle[s[0]][s[1]] = c * 7 + 4
        visited = set()
        visited.add(s)
        while s != e:
            for i, nxt in enumerate([
                (s[0] - 1, s[1]),
                (s[0] + 1, s[1]),
                (s[0], s[1] - 1),
                (s[0], s[1] + 1),
            ]):
                if 0 <= nxt[0] < n and 0 <= nxt[1] < m:
                    if color_board[nxt[0]][nxt[1]] == color_board[s[0]][s[1]] and nxt not in visited:
                        visited.add(nxt)
                        s = nxt
                        if s == e:
                            puzzle[s[0]][s[1]] = c * 7 + 4 # + i
                        else:
                            puzzle[s[0]][s[1]] = c * 7 + i
                        break
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
    # endpoints = [
    #     [(4, 4), (5, 7), 0],
    #     [(5, 2), (6, 7), 1],
    #     [(6, 3), (1, 6), 2],
    #     [(4, 2), (6, 6), 3],
    # ]
    # n = 8
    # m = 8
    endpoints, n, m = read_input("test_inputs/input.txt")
    sol = solve(endpoints, n, m)
    render(sol)