function getNeighbors([r, c]) {
    return [[r + 1, c], [r - 1, c], [r, c + 1], [r, c - 1]];
}

function dfsTest(puzzle, endpoints) {
    for (const [start, end] of endpoints) {
        const stack = [start.slice()];
        const visited = new Set();
        let found = false;
        while (stack.length) {
            const curr = stack.pop();
            const key = curr.toString();
            if (curr[0] === end[0] && curr[1] === end[1]) {
                found = true;
                break;
            }
            visited.add(key);
            for (const nxt of getNeighbors(curr)) {
                const [nr, nc] = nxt;
                if (nr < 0 || nr >= puzzle.length || nc < 0 || nc >= puzzle[0].length) continue;
                if ((puzzle[nr][nc] !== -1) && !(nr === end[0] && nc === end[1])) continue;
                const nkey = nxt.toString();
                if (!visited.has(nkey)) stack.push(nxt.slice());
            }
        }
        if (!found) return false;
    }
    return true;
}

function emptyTest3(puzzle, endpoints) {
    const viable = new Set();
    for (const [start, end] of endpoints) {
        const reach = pts => {
            const stack = [pts.slice()];
            const vis = new Set();
            while (stack.length) {
                const curr = stack.pop();
                const key = curr.toString();
                if (vis.has(key)) continue;
                vis.add(key);
                for (const nxt of getNeighbors(curr)) {
                    const [nr, nc] = nxt;
                    if (nr < 0 || nr >= puzzle.length || nc < 0 || nc >= puzzle[0].length) continue;
                    if (puzzle[nr][nc] !== -1) continue;
                    stack.push([nr, nc]);
                }
            }
            return vis;
        };
        const v1 = reach(start);
        const v2 = reach(end);
        for (const key of v1) {
            if (v2.has(key)) viable.add(key);
        }
    }
    const endpointsSet = new Set();
    endpoints.forEach(([s, e]) => { endpointsSet.add(s.toString()); endpointsSet.add(e.toString()); });
    for (let i = 0; i < puzzle.length; i++) {
        for (let j = 0; j < puzzle[0].length; j++) {
            if (puzzle[i][j] === -1) {
                const key = [i, j].toString();
                if (!viable.has(key)) return false;
                let numEmpty = 0;
                for (const neighbor of getNeighbors([i, j])) {
                    const [nr, nc] = neighbor;
                    if (nr < 0 || nr >= puzzle.length || nc < 0 || nc >= puzzle[0].length) continue;
                    if (puzzle[nr][nc] === -1 || endpointsSet.has(neighbor.toString())) numEmpty++;
                }
                if (numEmpty < 2) return false;
            }
        }
    }
    return true;
}

function solve(puzzle, endpoints, prev = -1) {
    let mostConstrained = 0;
    while (mostConstrained < endpoints.length &&
                 endpoints[mostConstrained][0].toString() === endpoints[mostConstrained][1].toString()) {
        mostConstrained++;
    }
    table.puzzle = puzzle;
    render(table.puzzle);
    if (mostConstrained === endpoints.length) {
        console.log('solved');
        return true;
    }
    console.log('most constrained', mostConstrained, endpoints[mostConstrained]);

    if (!dfsTest(puzzle, endpoints)) {
        console.log('partition check failed');
        return;
    }
    if (!emptyTest3(puzzle, endpoints)) {
        console.log('empty test failed');
        return;
    }

    const [start, end, color] = endpoints[mostConstrained];
    let nxts = getNeighbors(start);
    let indexed = nxts.map((nxt, i) => [i, nxt]);

    indexed.sort((a, b) => {
        const ia = a[0], ib = b[0];
        const na = a[1], nb = b[1];
        if (ia === prev) return -Infinity;
        if (ib === prev) return Infinity;
        return -((na[0] - end[0] + na[1] - end[1]) - (nb[0] - end[0] + nb[1] - end[1]));
    });

    // if direct path to end exists, explore only that
    for (let k = 0; k < 4; k++) {
        if (indexed[k][1].toString() === end.toString()) {
            indexed = [indexed[k]];
            break;
        }
    }

    function loop(idx) {
        if (idx >= indexed.length) return false;
        const [i, nxt] = indexed[idx];
        const [nr, nc] = nxt;
        if (nr < 0 || nr >= puzzle.length || nc < 0 || nc >= puzzle[0].length) return loop(idx + 1);
        if (puzzle[nr][nc] !== -1 && nxt.toString() !== end.toString()) return loop(idx + 1);

        // ensure not colliding with other endpoints
        if (endpoints.some(([s, e], idx) => idx !== mostConstrained &&
                (s.toString() === nxt.toString() || e.toString() === nxt.toString()))) return loop(idx + 1);

        // no adjacent same-color segments
        const neighs = getNeighbors(nxt);
        let conflict = false;
        for (const d of neighs) {
            if (d.toString() === start.toString() || d.toString() === end.toString()) continue;
            const [dr, dc] = d;
            if (dr < 0 || dr >= puzzle.length || dc < 0 || dc >= puzzle[0].length) continue;
            if (Math.floor(puzzle[dr][dc] / mapping.length) === color && puzzle[dr][dc] !== -1) {
                conflict = true;
                break;
            }
        }
        if (conflict) return loop(idx + 1);

        puzzle = structuredClone(puzzle);
        endpoints = structuredClone(endpoints);
        const origEndpoint = (puzzle[start[0]][start[1]] % mapping.length) === 4;
        if (!origEndpoint) puzzle[start[0]][start[1]] = color * mapping.length + i;
        else puzzle[start[0]][start[1]] = color * mapping.length + 5 + i;
        if (puzzle[nr][nc] === -1) puzzle[nr][nc] = color * mapping.length + i;

        endpoints[mostConstrained] = [nxt, end, color];
        setTimeout(() => {
            if (solve(puzzle, endpoints, i)) return true;
            endpoints[mostConstrained] = [start, end, color];

            if (!origEndpoint) puzzle[start[0]][start[1]] = -1;
            else puzzle[start[0]][start[1]] = color * mapping.length + 4;
            if (puzzle[nr][nc] === color * mapping.length + i) puzzle[nr][nc] = -1;
            loop(idx + 1);
        }, 10);
        // if (solve(puzzle, endpoints, i)) return true
    }
    loop(0);
    return false;
}

function build(endpoints, n, m) {
    const puzzle = Array.from({ length: n }, () => Array(m).fill(-1));
    endpoints.forEach(([s, e, color]) => {
        puzzle[s[0]][s[1]] = color * mapping.length + 4;
        puzzle[e[0]][e[1]] = color * mapping.length + 4;
    });
    return puzzle;
}