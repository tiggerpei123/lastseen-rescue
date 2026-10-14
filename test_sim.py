"""Basic checks. Run with:  python -m pytest   (or)   python tests/test_sim.py"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lastseen_sim import STRATEGIES, Building, ProbabilityMap, SimConfig, make_scenario, run_search  # noqa: E402

CFG = SimConfig()
B = Building(CFG)


def test_building_has_16_rooms():
    assert len(B) == 16
    assert B.rooms[0].name == "201" and B.rooms[-1].name == "216"


def test_scenarios_are_repeatable():
    a, b = make_scenario(B, CFG, 5), make_scenario(B, CFG, 5)
    assert [(v.room, v.last_seen_x) for v in a.victims] == [(v.room, v.last_seen_x) for v in b.victims]


def test_probabilities_are_valid():
    for seed in range(20):
        p = ProbabilityMap(B, CFG, make_scenario(B, CFG, seed)).p
        assert all(0.0 <= x <= 1.0 for x in p)


def test_empty_search_lowers_probability():
    pm = ProbabilityMap(B, CFG, make_scenario(B, CFG, 1))
    before = pm.p[3]
    pm.searched_and_empty(3)
    assert pm.p[3] < before


def test_every_strategy_runs_and_finds_people_only_where_they_are():
    for seed in range(20):
        sc = make_scenario(B, CFG, seed)
        rooms = {v.vid: v.room for v in sc.victims}
        for s in STRATEGIES:
            r = run_search(B, CFG, sc, s)
            assert r.end_time <= CFG.time_limit_s
            for vid in r.found_at:
                assert rooms[vid] in r.route


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok ", name)
