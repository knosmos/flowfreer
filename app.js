const mapping = ['link dn', 'link up', 'link rt', 'link lt', 'circle', 'link dn', 'link up', 'link rt', 'link lt']; // mod 7
const colors = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']; // red, green, yellow, blue, magenta, cyan, white, grey
let ctr = 0;

function render(puzzle) {
    let rendered = puzzle.map(row => row.map(i => {
        if (i === 5) return 'empty';
        let col = colors[Math.floor(i / mapping.length)];
        let ind = mapping[i % mapping.length];
        return `${ind} ${col}`;
    }));
    ctr++;
    table.$forceUpdate();
    return rendered;
}

function renderCell(cell) {
    if (cell === 5) return '';
    const col = colors[Math.floor(cell / mapping.length)];
    return `${mapping[cell % mapping.length]} ${col}`;
}

let table = new Vue({
    el: '#table',
    data: {
        puzzle: [],
        original: [],
        endpoints: [],
        n: 0,
        m: 0,
        num_placed: 0,
        last_placed: 0,
    },
    methods: {
        cellClass(cell) {
            if (cell === -1) return '';
            const col = colors[Math.floor(cell / mapping.length)];
            const ind = mapping[cell % mapping.length];
            return `${ind} ${col}`;
        },
        cellEndpoint(cell) {
            if (cell % mapping.length < 4) {
                return '';
            }
            const col = colors[Math.floor(cell / mapping.length)];
            return `circle ${col}`;
        },
        toggleCell(i, j) {
            if (this.puzzle[i][j] === -1) {
                this.puzzle[i][j] = Math.floor(this.num_placed / 2) * mapping.length + 4;
                this.num_placed++;
                if (this.num_placed % 2 === 0) {
                    this.endpoints.push([last_placed, [i, j], Math.floor((this.num_placed - 1) / 2)]);
                }
                last_placed = [i, j];
            }
            this.$forceUpdate();
        }
    }
});

function readInput() {
    const board = [
        "5........",
        ".......2.",
        ".........",
        ".6......3",
        "...5..6..",
        ".7.0.....",
        "...4..7..",
        "2.4.1....",
        "0.1..3..."
    ];
    // const board = [
    //     "3....40.1.",
    //     "..2.......",
    //     "..........",
    //     "..........",
    //     "..........",
    //     ".04.1.....",
    //     "...3......",
    //     ".......2..",
    //     "..........",
    //     ".........."
    // ];
    const endpointsDict = {};
    const n = board.length;
    const m = board[0].length;
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < m; j++) {
            const ch = board[i][j];
            if (ch === '.') continue;
            endpointsDict[ch] = endpointsDict[ch] || [];
            endpointsDict[ch].push([i, j]);
        }
    }
    const endpoints = [];
    for (const color in endpointsDict) {
        const coords = endpointsDict[color];
        if (coords.length !== 2) throw new Error(`Invalid input: ${color} has ${coords.length} endpoints`);
        endpoints.push([coords[0], coords[1], parseInt(color, 10)]);
    }
    return {endpoints, n, m};
}

function clearBoard() {
    let rows = parseInt(document.getElementById('rows').value); // will figure out vue later
    let cols = parseInt(document.getElementById('cols').value);
    table.puzzle = Array.from({ length: rows }, () => new Array(cols).fill(-1));
    table.endpoints = [];
    table.num_placed = 0;
    table.original = structuredClone(table.puzzle);
}

function solveBoard() {
    table.original = structuredClone(table.puzzle);
    solve(table.puzzle, table.endpoints, 0);
}

function resetBoard() {
    table.puzzle = structuredClone(table.original);
    table.$forceUpdate();
}

let input = readInput();
table.puzzle = build(input.endpoints, input.n, input.m);
table.original = structuredClone(table.puzzle);
table.endpoints = input.endpoints;
table.n = input.n;
table.m = input.m;
table.num_placed = input.endpoints.length * 2;
solveBoard();