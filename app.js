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
            return renderCell(cell);
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