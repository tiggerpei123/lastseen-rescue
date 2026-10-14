# Benchmark results (1000 simulated fires, seeds 0–999)

Simulation only, not field data. Times are seconds from crew entry. Anyone not found within 1200 s counts as 1200 s.

| Strategy | First victim (mean) | Each victim (mean) | All victims (median) | Not found in time |
|---|---:|---:|---:|---:|
| Current practice (nearest room first) | 231 s | 487 s | 736 s | 225 of 3485 |
| Current practice + dog alerts | 232 s | 467 s | 736 s | 84 of 3485 |
| LastSeen (CCTV + dog + thermal fused) | 124 s | 325 s | 512 s | 11 of 3485 |
| LastSeen, building without CCTV | 170 s | 384 s | 584 s | 11 of 3485 |

## Improvement

| Comparison | First victim | Each victim | All victims (median) | First victim: faster / same / slower |
|---|---:|---:|---:|---:|
| LastSeen vs current practice (nearest room first) | 46% (95% CI 43–49%) | 33% (95% CI 31–35%) | 30% | 624 / 192 / 184 of 1000 fires |
| LastSeen vs current practice + dog alerts | 46% (95% CI 44–49%) | 30% (95% CI 29–32%) | 30% | 626 / 191 / 183 of 1000 fires |
| LastSeen without CCTV vs current practice (nearest room first) | 26% (95% CI 24–28%) | 21% (95% CI 20–23%) | 21% | 543 / 324 / 133 of 1000 fires |

## Where the gain comes from

- Victims a camera saw before the smoke: LastSeen 271 s vs current practice 484 s on average.
- Victims no camera saw: LastSeen 402 s vs current practice 490 s (gain from fusing dog alerts and re-searching likely rooms).
- Building without CCTV: the planner alone reaches the first victim in 170 s vs 231 s.

95% confidence intervals come from resampling scenarios (bootstrap, 2,000 draws).
