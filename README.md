# Courier Planner

A self-contained Python prototype combining parcel prioritization, capacity-constrained package selection, shortest paths, and an approximate multi-stop delivery tour. It uses only the Python standard library.

## Run

Requires Python 3.9 or newer.

```bash
cd courier_planner
python3 courier_planner.py
python3 courier_planner.py --json --output evidence/sample_plan.json
python3 benchmark.py
```

Input is JSON (`data/sample.json`). `roads` is an undirected list of `[node_a, node_b, distance_km]`; all distances are positive. Each parcel has an ID, destination node, integer weight, integer priority value, and `HH:MM` deadline. One depot and one vehicle capacity define a single-trip planning problem. A parcel's value is its priority score; deadlines control display order, while priority is optimized by the knapsack.

## Algorithm design

1. **Priority sorting:** stable ordering by earliest deadline, highest priority, then parcel ID: `O(n log n)`.
2. **Packing:** 0/1 knapsack dynamic programming maximizes total priority within the integer capacity: `O(nC)` time and memory, where `C` is capacity in kg. The table is retained in memory for demonstration and reconstruction.
3. **Road graph:** adjacency lists represent an undirected weighted graph.
4. **Shortest paths:** heap-based Dijkstra is run from the depot and selected destinations. A shortest path expands each route leg, so the courier can travel through road nodes that are not delivery stops. Complexity per source is `O((V+E) log V)`.
5. **Delivery tour:** nearest-neighbor repeatedly chooses the closest remaining delivery stop based on Dijkstra distances, then returns to the depot. This is a practical TSP approximation, not a guaranteed optimal tour. Pairwise shortest-path preprocessing is approximately `O(K(V+E) log V)` for `K` selected destinations.

## Sample result

The sample uses 8 parcels, an 18 kg capacity, 9 graph nodes, and 25 undirected roads. The optimal DP selection has total priority 33 and weighs 18 kg. The nearest-neighbor tour through the selected destinations is `DEPOT → A → B → C → F → DEPOT`, with a computed distance of 20 km. Individual runtimes vary by machine and are printed on every run.

## Runtime evidence and limitations

`benchmark.py` creates deterministic synthetic workloads (seed 7) and records sort, knapsack (fixed capacity 40), and sparse-graph Dijkstra timings in `evidence/runtime.csv`; the accompanying SVG is `evidence/runtime.svg`. These are single local measurements, useful for order-of-growth illustration rather than a rigorous benchmark. Knapsack scales with numeric capacity, not merely parcel count. The route heuristic can return a longer tour than the optimum. The model assumes static roads, one vehicle, one delivery per selected parcel, no service times, and no time-window feasibility check.

## Project phases

- **Phase 1:** JSON schema, depot/parcel/road model, algorithm flow described above.
- **Phase 2:** deadline/priority ordering and DP-selected packing plan.
- **Phase 3:** graph, Dijkstra shortest-path legs, and nearest-neighbor tour.
- **Phase 4:** reproducible runtime CSV and chart.
- **Phase 5:** this guide, sample data, runnable output trace (`evidence/sample_output.txt`), and JSON result.

## Future improvements

Use a one-dimensional DP parent table to reduce memory; benchmark repeated runs and report medians; add local search (2-opt) after nearest-neighbor; incorporate time windows, service times, vehicle fleets, and road closures; and add a web interface for editing parcel and road data.
