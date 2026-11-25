# Design and execution flow

## Data model

| Entity | Fields | Purpose |
|---|---|---|
| Parcel | `id`, `destination`, `weight`, `priority`, `deadline` | Candidate delivery with a capacity cost, value, and urgency |
| Road | endpoint A, endpoint B, positive distance | Undirected edge in the customer/depot road graph |
| Vehicle | `capacity` | Maximum load for this trip |
| Plan | ranked parcels, selected parcels, route legs, distance, timings | Combined algorithm output |

## Pipeline

```text
JSON input
   ├─ parse deadlines ─ sort by deadline, priority, ID
   ├─ all parcels + capacity ─ 0/1 knapsack ─ selected delivery stops
   └─ roads ─ adjacency graph ─ Dijkstra distances ─ nearest-neighbor tour
                                                        └─ return to depot
Output: ranked queue, packed parcel list, stop sequence, road paths, distance, timings
```

The independent branches share the parcel records: sorting communicates delivery urgency to the dispatcher, while knapsack chooses the set that fits the vehicle and maximizes priority points. The route planner uses only selected destinations. It computes shortest road paths between the depot and every selected stop, then greedily orders stops by the nearest remaining one. Each leg includes its underlying road path so the route is actionable even when it crosses non-delivery nodes.

## Why these techniques

- Sorting gives predictable, explainable urgency ordering and runs in `O(n log n)`.
- 0/1 knapsack gives an exact optimum for the stated integer capacity/value model, with `O(nC)` cost.
- Dijkstra is suitable for positive road lengths and produces minimum-distance legs.
- Exact TSP search grows factorially with stop count. Nearest-neighbor provides a fast approximation and is appropriate for a small operational prototype; it has no general optimality guarantee.

## Validation evidence

The sample execution is captured in `evidence/sample_output.txt`, and the machine-readable result is in `evidence/sample_plan.json`. `benchmark.py` supplies deterministic synthetic size sweeps and emits `evidence/runtime.csv` plus `evidence/runtime.svg`. The sample's capacity check is 18 kg used out of 18 kg available; its chosen priority sum is 33. Every consecutive route leg is computed from Dijkstra, and the closed loop returns to `DEPOT`.
