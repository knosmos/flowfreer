function solve_with_sat(endpoints, n, m) {
    const clauses = [];
    const numColors = endpoints.length;

    function encode(i, j, k) {
        return (i * m + j) * numColors + k + 1;
    }

    function decode(x) {
        x -= 1;
        const k = x % numColors;
        x = Math.floor(x / numColors);
        const j = x % m;
        const i = Math.floor(x / m);
        return [i, j, k];
    }

    function getNeighbors(i, j) {
        const deltas = [[-1, 0], [1, 0], [0, -1], [0, 1]];
        return deltas
            .map(([di, dj]) => [i + di, j + dj])
            .filter(([ni, nj]) => ni >= 0 && ni < n && nj >= 0 && nj < m);
    }

    const endpointMapping = {};
    for (const [s, e, c] of endpoints) {
        endpointMapping[`${s[0]},${s[1]}`] = c;
        endpointMapping[`${e[0]},${e[1]}`] = c;
    }

    for (let i = 0; i < n; i++) {
        for (let j = 0; j < m; j++) {
            const key = `${i},${j}`;
            if (key in endpointMapping) {
                const c = endpointMapping[key];
                clauses.push([encode(i, j, c)]);
                for (let k = 0; k < numColors; k++) {
                    if (k != c) {
                        clauses.push([-encode(i, j, k)]);
                    }
                }
            } else {
                const allColors = [];
                for (let k = 0; k < numColors; k++) {
                    allColors.push(encode(i, j, k));
                }
                clauses.push(allColors);
                for (let k = 0; k < numColors; k++) {
                    for (let k2 = k + 1; k2 < numColors; k2++) {
                        clauses.push([-encode(i, j, k), -encode(i, j, k2)]);
                    }
                }
            }
        }
    }

    for (let i = 0; i < n; i++) {
        for (let j = 0; j < m; j++) {
            const neighbors = getNeighbors(i, j);
            const key = `${i},${j}`;
            if (key in endpointMapping) {
                const c = endpointMapping[key];
                clauses.push(neighbors.map(([ni, nj]) => encode(ni, nj, c)));
                for (let n1 = 0; n1 < neighbors.length; n1++) {
                    for (let n2 = n1 + 1; n2 < neighbors.length; n2++) {
                        const [ni1, nj1] = neighbors[n1];
                        const [ni2, nj2] = neighbors[n2];
                        clauses.push([-encode(ni1, nj1, c), -encode(ni2, nj2, c)]);
                    }
                }
            } else {
                for (let k = 0; k < numColors; k++) {
                    if (neighbors.length === 2) {
                        clauses.push([-encode(i, j, k), encode(neighbors[0][0], neighbors[0][1], k)]);
                        clauses.push([-encode(i, j, k), encode(neighbors[1][0], neighbors[1][1], k)]);
                    } else if (neighbors.length === 3) {
                        for (let n1 = 0; n1 < neighbors.length; n1++) {
                            for (let n2 = n1 + 1; n2 < neighbors.length; n2++) {
                                const [ni1, nj1] = neighbors[n1];
                                const [ni2, nj2] = neighbors[n2];
                                clauses.push([-encode(i, j, k), encode(ni1, nj1, k), encode(ni2, nj2, k)]);
                            }
                        }
                        clauses.push([-encode(i, j, k), ...neighbors.map(([ni, nj]) => -encode(ni, nj, k))]);
                    } else if (neighbors.length === 4) {
                        for (let n1 = 0; n1 < 4; n1++) {
                            for (let n2 = n1 + 1; n2 < 4; n2++) {
                                for (let n3 = n2 + 1; n3 < 4; n3++) {
                                    const [ni1, nj1] = neighbors[n1];
                                    const [ni2, nj2] = neighbors[n2];
                                    const [ni3, nj3] = neighbors[n3];
                                    clauses.push([
                                        -encode(i, j, k),
                                        -encode(ni1, nj1, k),
                                        -encode(ni2, nj2, k),
                                        -encode(ni3, nj3, k)
                                    ]);
                                    clauses.push([
                                        -encode(i, j, k),
                                        encode(ni1, nj1, k),
                                        encode(ni2, nj2, k),
                                        encode(ni3, nj3, k)
                                    ]);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    console.log("Clauses:", clauses.length);

    const solRaw = solveSAT(clauses);
    const colorBoard = Array.from({ length: n }, () => Array(m).fill(0));
    for (const x of solRaw) {
        if (x > 0) {
            const [i, j, k] = decode(x);
            colorBoard[i][j] = k;
        }
    }

    const puzzle = Array.from({ length: n }, () => Array(m).fill(0));
    for (const [start, end, c] of endpoints) {
        let s = start.slice(); // Clone
        puzzle[s[0]][s[1]] = c * mapping.length + 4;
        const visited = new Set();
        visited.add(`${s[0]},${s[1]}`);
        while (s[0] !== end[0] || s[1] !== end[1]) {
            const neighbors = [
                [s[0] - 1, s[1]],
                [s[0] + 1, s[1]],
                [s[0], s[1] - 1],
                [s[0], s[1] + 1]
            ];
            for (let i = 0; i < 4; i++) {
                const nxt = neighbors[i];
                if (
                    nxt[0] >= 0 && nxt[0] < n &&
                    nxt[1] >= 0 && nxt[1] < m &&
                    colorBoard[nxt[0]][nxt[1]] === colorBoard[s[0]][s[1]] &&
                    !visited.has(`${nxt[0]},${nxt[1]}`)
                ) {
                    visited.add(`${nxt[0]},${nxt[1]}`);
                    s = nxt;
                    if (s[0] === end[0] && s[1] === end[1]) {
                        puzzle[s[0]][s[1]] = c * mapping.length + 4 + i + 1;
                    } else {
                        puzzle[s[0]][s[1]] = c * mapping.length + i;
                    }
                    break;
                }
            }
        }
    }

    return puzzle;
}

function solveSAT(clauses) {
    // convert clauses to string format
    let clausesStr = clauses.map(clause => clause.join(' ') + ' 0').join('\n');
    clausesStr = 'p cnf ' + (clauses.length * 2) + ' ' + clauses.length + '\n' + clausesStr;
    console.log("SAT solver input:", clausesStr);
    let clausesStrLen = clausesStr.length;
    let solve_string = miniSatModule().cwrap('solve_string', 'string', ['string', 'int']);
    try {
        let result = solve_string(clausesStr, clausesStrLen);
        console.log("SAT solver result:", result);
        let vals = result.split(" ").slice(1).map(Number).filter(x => x > 0);
        console.log("Parsed lines:", vals);
        return vals;
    } catch(e) {
        console.error("Error in solveSAT:", e);
        return null;
    }
}