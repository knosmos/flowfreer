# flow freer
Solves Flow Free puzzles using SAT and dfs/recursive backtracking; also includes computer vision to extract boards. To my knowledge, this is the first browser-based Flow solver (play it online!) Using SAT, it's also incredibly fast: it solves boards on the order of a few hundred milliseconds.

## Why?
My friend is good at Flow Free and I am not :(( During a competition in Arizona, we spent a rare night off trying to analyze the math behind Flow (specifically, we were trying to determine the fewest number of colors needed to guarantee a unique solution for a given board size). I figured that writing a solver could give some insights.

## SAT
Flow is NP-complete, which means we can reduce (convert) any Flow board to a [Boolean Satisfiability problem](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem). Once we do this conversion, we can hand it off to an efficient SAT solver.

We represent each cell with a series of boolean variables $$v_{i,j,k}$$ such that the cell at position $$(i,j)$$ has color $$k$$ if $$v_{i,j,k}$$ is true. Now we want to encode the following conditions:

- each endpoint has its required color
- each endpoint has exactly one neighbor of the same color
- every other cell has exactly two neighbors of the same color (i.e., every non-endpoint cell has exactly one path going through it)

These conditions seem to be sufficient to handle all Flow boards. It intrinsically discounts paths where a color "space-fills" a rectangular region, since these would contain cells with at least three neighbors of the same color. These are never valid solutions in Flow, so we can ignore them.

### Each endpoint has its required color
We need to turn these conditions into something the SAT solver can understand. Specifically, we need to create a series of clauses in CNF form: each clause is a disjunction of literals, and the entire formula is a conjunction of clauses. The endpoint color condition is the easiest. For each endpoint, we create a clause $$[v_{i,j,k}]$$ where $$k$$ is the color of the endpoint. This means that the endpoint must be colored with its required color, and clauses $$[-v_{i,j,c}]$$ for all other colors $$c$$.

### Each endpoint has one neighbor of the same color
We first create a clause $$[v_{x_1,y_2,k},v_{x_2,y_2,k},\dots,v_{x_4,y_4,k}]$$ where $$k$$ is the color of the endpoint and $$x_i,y_i$$ are the coordinates of the four neighbors of the endpoint. This means that at least one of the neighbors must be colored with the same color as the endpoint. We also create clauses $$[-v_{x_a,y_a,k},-v_{x_b,y_b,k}]$$ for all pairs of neighbors $$a,b$$ of the endpoint. This means that at most one of the neighbors can be colored with the same color as the endpoint.

### Every normal cell has exactly two neighbors of the same color
This is the trickiest encoding, and I solve this with a rather tedious approach. For a given non-endpoint cell $$(i,j)$$, we iterate over all colors $$k$$. Based on the cell's number of adjacent neighbors, we create an encoding that forces the cell to either not have color $$k$$ or have two neighbors of color $$k$$.

- If the cell has two neighbors, we create two clauses $$[-v_{i,j,k},v_{x_1,y_1,k}]$$ and $$[-v_{i,j,k},v_{x_2,y_2,k}]$$ where $$x_1,y_1$$ and $$x_2,y_2$$ are the coordinates of the two neighbors. This means that if the cell has color $$k$$, then both neighbors must also have color $$k$$.

- If the cell has three neighbors, we create clauses that forces one of any group of two neighbors to be colored with color $$k$$, and a clause that ensures the three neighbors are not all colored with color $$k$$.

- If the cell has four neighbors, we create clauses that forces one of any group of three neighbors to be colored with color $$k$$, and a clause that forces one of any group of three neighbors to *not* be colored with color $$k$$.

After handing the completed CNF formula to [Minisat](http://minisat.se/), we get a coloring of the Flow board. We run a simple search from each endpoint to determine the actual paths taken by each color.

## Heuristic Pathing
We can also use a heuristic pathing algorithm to solve Flow boards. This is a recursive backtracking algorithm that tries to fill in the board one color at a time. This is the first algorithm I came up with when trying to solve Flow, and it's several orders of magnitude slower than the SAT solver. However, I spent about two days writing it, so here it will stay. It also has a much nicer visualization of the solving process. We encode the following checks:

- Routability: after each step, we check that every color that has not been routed has a valid path between its endpoints. This is done by running a DFS from each endpoint and checking that the other endpoint is reachable.
- Empty space: Flow solutions are not allowed to have empty squares, so we check that every empty square could potentially be filled by a color. This is done by checking that there exists a pair of endpoints such that there exists a path from the first endpoint to the empty square and from the empty square to the second endpoint.
- Space-filling: no color has more than two neighbors of the same color.

We also attempt some heuristics to speed up the search. For example, we try to fill in the most constrained colors first (i.e., colors with the fewest possible paths). In practice, this seems to give minimal benefit. If I wrote the solver to use a priority queue rather than pure BFS, it would likely be much faster.

## Computer Vision
I got annoyed with manually entering Flow boards, so I wrote a simple computer vision algorithm to extract puzzles from screenshots. Using OpenCV, it crops the main board (removing all the UI elements) using contour detection. It then runs Sobel-X edge detection and Hough Lines to find vertical grid lines that can extract the size of the grid. From here, it samples the colors of each cell and tries to match close colors together. The vision algorithm is built into the website; you can also [run it standalone](https://knosmos.github.io/flowfreer/cv) to see some of its internal workings.