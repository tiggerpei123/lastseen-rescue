"""Turn search results into the numbers we report."""

import random
import statistics as st

from .config import SimConfig
from .scenario import Scenario
from .simulate import SearchResult


def victim_times(cfg: SimConfig, scenario: Scenario, result: SearchResult) -> list[float]:
    """Seconds until each victim was found. Anyone not found counts as the time limit."""
    return [result.found_at.get(v.vid, cfg.time_limit_s) for v in scenario.victims]


def scenario_row(cfg: SimConfig, scenario: Scenario, result: SearchResult) -> dict:
    times = victim_times(cfg, scenario, result)
    seen = [t for v, t in zip(scenario.victims, times) if v.seen_on_cctv]
    unseen = [t for v, t in zip(scenario.victims, times) if not v.seen_on_cctv]
    return {
        "seed": scenario.seed,
        "strategy": result.strategy,
        "victims": len(times),
        "victims_seen_on_cctv": len(seen),
        "first_victim_s": min(times),
        "mean_victim_s": st.mean(times),
        "all_victims_s": max(times),
        "not_found": sum(v.vid not in result.found_at for v in scenario.victims),
        "rooms_searched": len(result.route),
        "_times": times,
        "_seen": seen,
        "_unseen": unseen,
    }


def summarise(rows: list[dict]) -> dict:
    all_times = [t for r in rows for t in r["_times"]]
    seen = [t for r in rows for t in r["_seen"]]
    unseen = [t for r in rows for t in r["_unseen"]]
    return {
        "scenarios": len(rows),
        "victims": len(all_times),
        "first_victim_mean_s": st.mean(r["first_victim_s"] for r in rows),
        "each_victim_mean_s": st.mean(all_times),
        "all_victims_median_s": st.median(r["all_victims_s"] for r in rows),
        "not_found_in_time": sum(r["not_found"] for r in rows),
        "seen_victim_mean_s": st.mean(seen) if seen else float("nan"),
        "unseen_victim_mean_s": st.mean(unseen) if unseen else float("nan"),
    }


def pct_faster(new: float, old: float) -> float:
    return 100.0 * (old - new) / old


def bootstrap_ci(groups: list[tuple[float, float, int]], n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    """95% interval for '% faster', resampling whole scenarios.

    Each group is (sum of new times, sum of old times, number of times) for one scenario,
    so the interval matches the pooled mean used for the headline number.
    """
    rng = random.Random(seed)
    k = len(groups)
    vals = []
    for _ in range(n_boot):
        sample = [groups[rng.randrange(k)] for _ in range(k)]
        new = sum(g[0] for g in sample)
        old = sum(g[1] for g in sample)
        vals.append(pct_faster(new, old))
    vals.sort()
    return vals[int(0.025 * n_boot)], vals[int(0.975 * n_boot) - 1]
