function solve(endpoints, n, m) {
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
                    if (k !== c) {
                        clauses.push([-encode(i, j, k)]);
                    }
                }
            } else {
                clauses.push([...Array(numColors).keys()].map(k => encode(i, j, k)));
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
                                    clauses.push([-encode(i, j, k), -encode(ni1, nj1, k), -encode(ni2, nj2, k), -encode(ni3, nj3, k)]);
                                    clauses.push([-encode(i, j, k), encode(ni1, nj1, k), encode(ni2, nj2, k), encode(ni3, nj3, k)]);
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    const solRaw = solveSAT(clauses);
    const solDecoded = [];
    for (const x of solRaw) {
        if (x > 0) {
            solDecoded.push(decode(x));
        }
    }
    return solDecoded;
}

function solveSAT(clauses) {
    // convert clauses to string format
    let clausesStr = clauses.map(clause => clause.join(' ')).join('\n') + '\n0\n';
    let clausesStrLen = clausesStr.length;
    let solve_string = Module.cwrap('solve_string', 'string', ['string', 'int']);
    try {
        let result = solve_string(clausesStr, clausesStrLen);
        console.log("SAT solver result:", result);
    } catch(e) {
        console.error("Error in solveSAT:", e);
        return null;
    }
  }
