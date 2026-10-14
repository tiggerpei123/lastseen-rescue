"""Benchmark: compare search strategies over many random fire scenarios.

    python run_benchmark.py                  # 1000 scenarios (headline numbers)
    python run_benchmark.py --scenarios 30   # quick run

Writes per-scenario results, a summary and a chart to results/.
"""

import argparse
import csv
import json
import os

from lastseen_sim import STRATEGIES, Building, SimConfig, make_scenario, run_search
from lastseen_sim.metrics import bootstrap_ci, pct_faster, scenario_row, summarise

LABELS = {
    "nearest": "Current practice (nearest room first)",
    "nearest_k9": "Current practice + dog alerts",
    "lastseen": "LastSeen (CCTV + dog + thermal fused)",
    "lastseen_no_cctv": "LastSeen, building without CCTV",
}


def run(n: int, start_seed: int, cfg: SimConfig):
    building = Building(cfg)
    rows = {s: [] for s in STRATEGIES}
    for seed in range(start_seed, start_seed + n):
        scenario = make_scenario(building, cfg, seed)
        for s in STRATEGIES:
            result = run_search(building, cfg, scenario, s)
            rows[s].append(scenario_row(cfg, scenario, result))
    return rows


def compare(rows, new="lastseen", old="nearest"):
    a, b = rows[new], rows[old]
    first_pairs = [(x["first_victim_s"], y["first_victim_s"], 1) for x, y in zip(a, b)]
    each_pairs = [(sum(x["_times"]), sum(y["_times"]), len(x["_times"])) for x, y in zip(a, b)]
    sa, sb = summarise(a), summarise(b)
    wins = sum(x < y for x, y, _ in first_pairs)
    ties = sum(x == y for x, y, _ in first_pairs)
    return {
        "vs": old,
        "first_victim_pct_faster": pct_faster(sa["first_victim_mean_s"], sb["first_victim_mean_s"]),
        "first_victim_ci95": bootstrap_ci(first_pairs),
        "each_victim_pct_faster": pct_faster(sa["each_victim_mean_s"], sb["each_victim_mean_s"]),
        "each_victim_ci95": bootstrap_ci(each_pairs),
        "all_victims_pct_faster": pct_faster(sa["all_victims_median_s"], sb["all_victims_median_s"]),
        "first_victim_wins": wins,
        "first_victim_ties": ties,
        "first_victim_losses": len(first_pairs) - wins - ties,
        "scenarios": len(a),
    }


def write_outputs(rows, out_dir: str, cfg: SimConfig, n: int, start_seed: int, plots: bool):
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "per_scenario.csv"), "w", newline="") as f:
        fields = [k for k in rows["nearest"][0] if not k.startswith("_")]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for s in STRATEGIES:
            for r in rows[s]:
                w.writerow({k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items() if k in fields})

    summary = {s: summarise(rows[s]) for s in STRATEGIES}
    comparisons = [compare(rows, "lastseen", "nearest"), compare(rows, "lastseen", "nearest_k9"),
                   compare(rows, "lastseen_no_cctv", "nearest")]
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump({"config": cfg.__dict__, "scenarios": n, "start_seed": start_seed,
                   "summary": summary, "comparisons": comparisons}, f, indent=2)

    lines = [
        f"# Benchmark results ({n} simulated fires, seeds {start_seed}–{start_seed + n - 1})",
        "",
        "Simulation only, not field data. Times are seconds from crew entry. "
        f"Anyone not found within {cfg.time_limit_s:.0f} s counts as {cfg.time_limit_s:.0f} s.",
        "",
        "| Strategy | First victim (mean) | Each victim (mean) | All victims (median) | Not found in time |",
        "|---|---:|---:|---:|---:|",
    ]
    for s in STRATEGIES:
        m = summary[s]
        lines.append(f"| {LABELS[s]} | {m['first_victim_mean_s']:.0f} s | {m['each_victim_mean_s']:.0f} s | "
                     f"{m['all_victims_median_s']:.0f} s | {m['not_found_in_time']} of {m['victims']} |")
    lines += ["", "## Improvement", "",
              "| Comparison | First victim | Each victim | All victims (median) | First victim: faster / same / slower |",
              "|---|---:|---:|---:|---:|"]
    for c in comparisons:
        new = "LastSeen" if c is not comparisons[2] else "LastSeen without CCTV"
        lo1, hi1 = c["first_victim_ci95"]
        lo2, hi2 = c["each_victim_ci95"]
        lines.append(
            f"| {new} vs {LABELS[c['vs']].lower()} | {c['first_victim_pct_faster']:.0f}% (95% CI {lo1:.0f}–{hi1:.0f}%) | "
            f"{c['each_victim_pct_faster']:.0f}% (95% CI {lo2:.0f}–{hi2:.0f}%) | {c['all_victims_pct_faster']:.0f}% | "
            f"{c['first_victim_wins']} / {c['first_victim_ties']} / {c['first_victim_losses']} of {c['scenarios']} fires |")
    m_ls, m_nc, m_nr = summary["lastseen"], summary["lastseen_no_cctv"], summary["nearest"]
    lines += ["", "## Where the gain comes from", "",
              f"- Victims a camera saw before the smoke: LastSeen {m_ls['seen_victim_mean_s']:.0f} s vs current practice "
              f"{m_nr['seen_victim_mean_s']:.0f} s on average.",
              f"- Victims no camera saw: LastSeen {m_ls['unseen_victim_mean_s']:.0f} s vs current practice "
              f"{m_nr['unseen_victim_mean_s']:.0f} s (gain from fusing dog alerts and re-searching likely rooms).",
              f"- Building without CCTV: the planner alone reaches the first victim in {m_nc['first_victim_mean_s']:.0f} s "
              f"vs {m_nr['first_victim_mean_s']:.0f} s.",
              "", "95% confidence intervals come from resampling scenarios (bootstrap, 2,000 draws)."]
    with open(os.path.join(out_dir, "summary.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    if plots:
        from plots import benchmark_chart
        benchmark_chart(summary, os.path.join(out_dir, "benchmark_chart.png"), n)
    return summary, comparisons


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenarios", type=int, default=1000)
    ap.add_argument("--start-seed", type=int, default=0)
    ap.add_argument("--out", default="results")
    ap.add_argument("--no-plots", action="store_true", help="skip charts (no matplotlib needed)")
    args = ap.parse_args()

    cfg = SimConfig()
    rows = run(args.scenarios, args.start_seed, cfg)
    write_outputs(rows, args.out, cfg, args.scenarios, args.start_seed, plots=not args.no_plots)
    print(open(os.path.join(args.out, "summary.md")).read())


if __name__ == "__main__":
    main()
