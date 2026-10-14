"""Draw one scenario: the probability map and the search order of each strategy.

    python run_example.py --seed 7
"""

import argparse
import os

from lastseen_sim import Building, ProbabilityMap, SimConfig, make_scenario, run_search
from plots import example_map


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="results/example_map.png")
    args = ap.parse_args()

    cfg = SimConfig()
    b = Building(cfg)
    sc = make_scenario(b, cfg, args.seed)
    start_map = ProbabilityMap(b, cfg, sc, use_cctv=True).p
    res = {s: run_search(b, cfg, sc, s) for s in ("nearest", "lastseen")}

    print(f"Scenario {args.seed}: {len(sc.victims)} trapped")
    for v in sc.victims:
        seen = f"last seen at x={v.last_seen_x:.1f} m heading {'+' if v.heading > 0 else '-'}" if v.seen_on_cctv else "not seen on CCTV"
        print(f"  person {v.vid} in room {b.rooms[v.room].name}, {seen}")
    for s, r in res.items():
        found = ", ".join(f"person {k} at {t:.0f} s" for k, t in sorted(r.found_at.items(), key=lambda kv: kv[1]))
        print(f"  {s:9s} route {[b.rooms[i].name for i in r.route[:8]]} ... found: {found}")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    def first(r):
        return min(r.found_at.values()) if r.found_at else cfg.time_limit_s
    panels = [(f"Current practice (nearest room first): first person found at {first(res['nearest']):.0f} s",
               res["nearest"].route, False),
              (f"LastSeen: first person found at {first(res['lastseen']):.0f} s",
               res["lastseen"].route, True)]
    example_map(b, cfg, sc, start_map, panels, args.out)
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
