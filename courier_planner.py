#!/usr/bin/env python3
"""Courier planning demo: priority sorting, 0/1 knapsack, Dijkstra, NN-TSP."""
from __future__ import annotations
import argparse, heapq, json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load_data(path):
    with open(path, encoding="utf-8") as f: data = json.load(f)
    for p in data["parcels"]:
        h, m = map(int, p["deadline"].split(":")); p["deadline_min"] = h * 60 + m
    return data

def prioritize(parcels):
    return sorted(parcels, key=lambda p: (p["deadline_min"], -p["priority"], p["id"]))

def pack(parcels, capacity):
    """0/1 knapsack maximizing total priority; returns chosen ids and DP table."""
    n = len(parcels); dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i, p in enumerate(parcels, 1):
        for cap in range(capacity + 1):
            dp[i][cap] = dp[i-1][cap]
            if p["weight"] <= cap:
                dp[i][cap] = max(dp[i][cap], dp[i-1][cap-p["weight"]] + p["priority"])
    chosen=[]; cap=capacity
    for i in range(n, 0, -1):
        if dp[i][cap] != dp[i-1][cap]:
            chosen.append(parcels[i-1]); cap -= parcels[i-1]["weight"]
    chosen.reverse()
    return chosen, dp

def graph_from_roads(roads):
    graph={}
    for a,b,w in roads:
        graph.setdefault(a,[]).append((b,w)); graph.setdefault(b,[]).append((a,w))
    return graph

def dijkstra(graph, source):
    dist={v: float("inf") for v in graph}; prev={}; dist[source]=0; queue=[(0,source)]
    while queue:
        d,u=heapq.heappop(queue)
        if d != dist[u]: continue
        for v,w in graph[u]:
            nd=d+w
            if nd < dist[v]: dist[v]=nd; prev[v]=u; heapq.heappush(queue,(nd,v))
    return dist,prev

def path_between(prev, source, target):
    if source == target: return [source]
    if target not in prev: raise ValueError(f"No path from {source} to {target}")
    out=[target]
    while out[-1] != source: out.append(prev[out[-1]])
    return out[::-1]

def route(graph, depot, destinations):
    """Nearest-neighbor TSP approximation over Dijkstra shortest-path distances."""
    vertices=set(graph)
    if not set(destinations) <= vertices or depot not in vertices: raise ValueError("Unknown route node")
    sources=[depot]+list(dict.fromkeys(destinations)); metrics={s:dijkstra(graph,s) for s in sources}
    remaining=set(destinations); current=depot; stops=[depot]; legs=[]; total=0
    while remaining:
        nxt=min(remaining, key=lambda v:(metrics[current][0][v],v))
        dist,prev=metrics[current]; leg=path_between(prev,current,nxt)
        legs.append({"from":current,"to":nxt,"distance":dist[nxt],"path":leg})
        total+=dist[nxt]; stops.append(nxt); remaining.remove(nxt); current=nxt
    dist,prev=metrics[current]; leg=path_between(prev,current,depot)
    legs.append({"from":current,"to":depot,"distance":dist[depot],"path":leg})
    total+=dist[depot]; stops.append(depot)
    return {"stops":stops,"legs":legs,"distance":total}

def plan(data):
    timings={}
    t=time.perf_counter(); ranked=prioritize(data["parcels"]); timings["priority_sort_ms"]=(time.perf_counter()-t)*1000
    t=time.perf_counter(); chosen,dp=pack(ranked,data["capacity"]); timings["knapsack_dp_ms"]=(time.perf_counter()-t)*1000
    graph=graph_from_roads(data["roads"]); t=time.perf_counter()
    trip=route(graph,data["depot"],[p["destination"] for p in chosen]); timings["shortest_paths_and_route_ms"]=(time.perf_counter()-t)*1000
    return {"ranked":ranked,"selected":chosen,"capacity":data["capacity"],"used_weight":sum(p["weight"] for p in chosen),"total_priority":sum(p["priority"] for p in chosen),"route":trip,"timings_ms":timings,"dp":dp}

def render(result):
    lines=["COURIER PLAN", "="*60, f"Vehicle capacity: {result['capacity']} kg | Loaded: {result['used_weight']} kg | Priority value: {result['total_priority']}", "", "Priority queue (deadline, then priority):"]
    lines += [f"  {p['id']:5} → {p['destination']}  {p['weight']:2} kg  priority {p['priority']:2}  deadline {p['deadline']}" for p in result["ranked"]]
    lines += ["", "Selected parcels (0/1 knapsack):"]
    lines += [f"  {p['id']} → {p['destination']} ({p['weight']} kg, value {p['priority']})" for p in result["selected"]]
    lines += ["", "Delivery route (nearest-neighbor over shortest paths):", "  " + " → ".join(result["route"]["stops"]), f"Total distance: {result['route']['distance']} km", "", "Timing (single run; machine dependent):"]
    lines += [f"  {k}: {v:.4f} ms" for k,v in result["timings_ms"].items()]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--input",default=str(ROOT/"data/sample.json")); ap.add_argument("--json",action="store_true"); ap.add_argument("--output",help="write plan JSON")
    args=ap.parse_args(); result=plan(load_data(args.input))
    if args.output: Path(args.output).write_text(json.dumps({k:v for k,v in result.items() if k!="dp"},indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="dp"},indent=2) if args.json else render(result))
if __name__ == "__main__": main()
