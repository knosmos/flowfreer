const mapping = ['link dn', 'link up', 'link rt', 'link lt', 'circle', 'link dn', 'link up', 'link rt', 'link lt']; // mod 7
const colors = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']; // red, green, yellow, blue, magenta, cyan, white, grey
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
        endpoints: [],
        n: 0,
        m: 0,
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
            this.puzzle[i][j] = this.puzzle[i][j] === 1 ? 0 : 1;
            console.log(`Cell (${i}, ${j}) toggled to ${this.puzzle[i][j]}`);
            this.$forceUpdate();
        }
    }
});

let input = readInput();
table.puzzle = build(input.endpoints, input.n, input.m);
table.endpoints = input.endpoints;
table.n = input.n;
table.m = input.m;
solve(table.puzzle, table.endpoints, 0);
table.$forceUpdate();