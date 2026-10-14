"""Sensitivity: does the result still hold when our assumptions are wrong?

    python run_sensitivity.py              # 500 scenarios per setting

Changes one assumption at a time and reports how much faster LastSeen is than
current practice (nearest room first). Writes results/sensitivity.md.
"""

import argparse
import dataclasses
import os

from lastseen_sim import Building, SimConfig, make_scenario, run_search
from lastseen_sim.metrics import pct_faster, scenario_row, summarise

SWEEPS = [
    ("p_seen_on_cctv", "Share of occupants seen on CCTV", [0.0, 0.3, 0.6, 0.9]),
    ("p_heading_correct", "Walking direction read correctly", [0.5, 0.85, 1.0]),
    ("prior_sigma_m", "Spread of the last-seen guess (m)", [1.5, 3.0, 6.0]),
    ("p_thermal_detect", "Thermal search finds a person in the room", [0.7, 0.85, 0.95]),
    ("p_k9_alert_true", "Dog alerts at an occupied room", [0.3, 0.6, 0.9]),
    ("room_search_s", "Seconds to search one room", [20.0, 40.0, 60.0]),
    ("rooms_per_side", "Rooms per side of the corridor", [4, 8, 12]),
]


def measure(cfg: SimConfig, n: int):
    b = Building(cfg)
    ls, nr = [], []
    for seed in range(n):
        sc = make_scenario(b, cfg, seed)
        ls.append(scenario_row(cfg, sc, run_search(b, cfg, sc, "lastseen")))
        nr.append(scenario_row(cfg, sc, run_search(b, cfg, sc, "nearest")))
    a, c = summarise(ls), summarise(nr)
    return (pct_faster(a["first_victim_mean_s"], c["first_victim_mean_s"]),
            pct_faster(a["each_victim_mean_s"], c["each_victim_mean_s"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", type=int, default=500)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    base = SimConfig()
    lines = [f"# Sensitivity analysis ({args.scenarios} simulated fires per setting)", "",
             "LastSeen vs current practice (nearest room first). One assumption changed at a time; "
             "the default value is in bold.", "",
             "| Assumption | Value | First victim | Each victim |", "|---|---:|---:|---:|"]
    for field, label, values in SWEEPS:
        for val in values:
            cfg = dataclasses.replace(base, **{field: val})
            f1, f2 = measure(cfg, args.scenarios)
            shown = f"**{val}**" if val == getattr(base, field) else f"{val}"
            lines.append(f"| {label} | {shown} | {f1:.0f}% faster | {f2:.0f}% faster |")
            print(lines[-1], flush=True)
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "sensitivity.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
