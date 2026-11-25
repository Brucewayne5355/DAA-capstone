"""Generate a reproducible runtime comparison CSV and SVG chart."""
import csv, random, time
from pathlib import Path
from courier_planner import prioritize, pack, graph_from_roads, dijkstra

OUT=Path(__file__).resolve().parent/"evidence"
random.seed(7)
rows=[]
for n in (8, 20, 40, 80, 160):
    parcels=[{"id":f"P{i}","deadline_min":random.randrange(480,1080),"priority":random.randrange(1,11),"weight":random.randrange(1,11)} for i in range(n)]
    t=time.perf_counter(); prioritize(parcels); sort_ms=(time.perf_counter()-t)*1000
    t=time.perf_counter(); pack(parcels,40); dp_ms=(time.perf_counter()-t)*1000
    # Sparse undirected road graph; time one shortest-path run on its largest component.
    roads=[(str(i),str(i+1),random.randrange(1,20)) for i in range(n-1)]
    roads += [(str(i),str(i+2),random.randrange(1,20)) for i in range(n-2)]
    graph=graph_from_roads(roads); t=time.perf_counter(); dijkstra(graph,"0"); graph_ms=(time.perf_counter()-t)*1000
    rows.append((n,sort_ms,dp_ms,graph_ms))
with open(OUT/"runtime.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["parcel_count","priority_sort_ms","knapsack_capacity_40_ms","dijkstra_sparse_graph_ms"]); w.writerows(rows)
# Dependency-free SVG line chart.
W,H=820,440; left,top,right,bottom=75,35,25,65
maxv=max(max(r[1:]) for r in rows)*1.15 or 1
colors=["#1976d2","#e67e22","#2e9d70"]; names=["Priority sort","Knapsack DP (capacity 40)","Dijkstra (sparse graph)"]
def xy(i,val): return left+i*(W-left-right)/(len(rows)-1), H-bottom-val/maxv*(H-top-bottom)
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/><text x="{W/2}" y="24" text-anchor="middle" font-family="Arial" font-size="19" font-weight="bold">Runtime by input size</text>']
for j in range(5):
    y=top+j*(H-top-bottom)/4; val=maxv*(4-j)/4
    s.append(f'<line x1="{left}" y1="{y}" x2="{W-right}" y2="{y}" stroke="#ddd"/><text x="{left-9}" y="{y+4}" text-anchor="end" font-family="Arial" font-size="11">{val:.3f}</text>')
s += [f'<line x1="{left}" y1="{top}" x2="{left}" y2="{H-bottom}" stroke="#333"/>',f'<line x1="{left}" y1="{H-bottom}" x2="{W-right}" y2="{H-bottom}" stroke="#333"/>']
for i,r in enumerate(rows):
    x,_=xy(i,0); s.append(f'<text x="{x}" y="{H-bottom+22}" text-anchor="middle" font-family="Arial" font-size="12">{r[0]}</text>')
for k,(name,color) in enumerate(zip(names,colors),1):
    pts=[xy(i,r[k]) for i,r in enumerate(rows)]
    s.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" points="'+" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)+'"/>')
    for x,y in pts: s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
    lx=left+(k-1)*230; s.append(f'<line x1="{lx}" y1="{H-20}" x2="{lx+22}" y2="{H-20}" stroke="{color}" stroke-width="3"/><text x="{lx+29}" y="{H-16}" font-family="Arial" font-size="12">{name}</text>')
s.append(f'<text x="18" y="{H/2}" transform="rotate(-90 18 {H/2})" text-anchor="middle" font-family="Arial" font-size="13">Elapsed time (ms)</text><text x="{W/2}" y="{H-40}" text-anchor="middle" font-family="Arial" font-size="13">Parcel / graph vertex count</text></svg>')
(OUT/"runtime.svg").write_text("".join(s),encoding="utf-8")
print("Wrote evidence/runtime.csv and evidence/runtime.svg")
