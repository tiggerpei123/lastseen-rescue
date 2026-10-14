"""Run one search of one scenario with one strategy.

Search strategies
-----------------
nearest      Current practice: search the nearest room not yet searched, then sweep again.
nearest_k9   Current practice plus the dog: go to a room as soon as the dog alerts at it.
lastseen     LastSeen: always go where (chance someone is there) / (time to get there and search)
             is highest, using the fused probability map (CCTV + dog + previous searches).
lastseen_no_cctv  The same planner when the building has no CCTV (map starts flat).

Fairness: every strategy faces the same scenario and the same sensor luck. A sensor outcome
is drawn from a random stream keyed by (scenario, sensor, room or person, visit number),
so "the thermal camera misses person 2 on the first visit to room 205" happens for every
strategy that visits room 205 for the first time.
"""

import random
from dataclasses import dataclass, field

from .building import Building
from .config import SimConfig
from .probability_map import ProbabilityMap
from .scenario import Scenario

STRATEGIES = ("nearest", "nearest_k9", "lastseen", "lastseen_no_cctv")


def _draw(seed: int, *keys) -> float:
    """A repeatable random number in [0, 1) for one sensor event."""
    return random.Random("-".join(str(k) for k in (seed,) + keys)).random()


@dataclass
class SearchResult:
    strategy: str
    found_at: dict[int, float] = field(default_factory=dict)   # victim id -> seconds after entry
    route: list[int] = field(default_factory=list)              # rooms searched, in order
    end_time: float = 0.0


def run_search(building: Building, cfg: SimConfig, scenario: Scenario, strategy: str) -> SearchResult:
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown strategy {strategy!r}")

    pmap = ProbabilityMap(building, cfg, scenario, use_cctv=(strategy == "lastseen"))
    visits = [0] * len(building)      # how many times each room has been searched
    dog_passes = [0] * len(building)  # how many times the dog has passed each door
    alerted: set[int] = set()         # rooms the dog alerted at, not searched since
    unfound = {v.vid: v for v in scenario.victims}
    result = SearchResult(strategy=strategy)

    t, x, side = 0.0, 0.0, None       # the crew starts at the stairwell entry

    while unfound and t < cfg.time_limit_s:
        room = _choose(strategy, building, cfg, pmap, visits, alerted, x, side)

        # Move to the door. The dog sniffs every door on the way.
        t += building.travel_time(x, side, room)
        for r in building.doors_passed(x, room.door_x):
            occupied = any(v.room == r.index for v in unfound.values())
            p_alert = cfg.p_k9_alert_true if occupied else cfg.p_k9_alert_false
            alert = _draw(scenario.seed, "k9", r.index, dog_passes[r.index]) < p_alert
            dog_passes[r.index] += 1
            pmap.dog_passed(r.index, alert)
            if alert:
                alerted.add(r.index)
        x, side = room.door_x, room.side

        # Search the room.
        t += cfg.room_search_s
        if t > cfg.time_limit_s:
            break
        k = visits[room.index]
        visits[room.index] += 1
        result.route.append(room.index)
        alerted.discard(room.index)
        hits = [
            v for v in unfound.values()
            if v.room == room.index and _draw(scenario.seed, "thermal", v.vid, k) < cfg.p_thermal_detect
        ]
        for v in hits:
            result.found_at[v.vid] = t
            del unfound[v.vid]
        if hits:
            pmap.searched_and_found(room.index)
        else:
            pmap.searched_and_empty(room.index)

    result.end_time = min(t, cfg.time_limit_s)
    return result


def _choose(strategy, building, cfg, pmap, visits, alerted, x, side):
    rooms = building.rooms

    def nearest(candidates):
        return min(candidates, key=lambda r: (building.travel_time(x, side, r), r.index))

    if strategy in ("nearest", "nearest_k9"):
        if strategy == "nearest_k9" and alerted:
            return nearest([rooms[i] for i in alerted])
        fewest = min(visits)                      # first sweep, then second sweep, ...
        return nearest([r for r in rooms if visits[r.index] == fewest])

    # LastSeen planner: best expected find per second.
    def score(r):
        cost = building.travel_time(x, side, r) + cfg.room_search_s
        return pmap.p[r.index] / cost

    return max(rooms, key=lambda r: (score(r), -r.index))
