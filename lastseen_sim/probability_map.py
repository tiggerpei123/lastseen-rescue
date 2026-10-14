"""The LastSeen probability map: for every room, the chance that someone is still trapped there.

It starts from CCTV last-seen tracks, then is updated by every search and every dog pass.
The same code is meant to run on the command-vehicle host in Stage II.
"""

import math

from .building import Building
from .config import SimConfig
from .scenario import Scenario


def _to_odds(p: float) -> float:
    p = min(max(p, 1e-9), 1 - 1e-9)
    return p / (1 - p)


def _from_odds(o: float) -> float:
    return o / (1 + o)


class ProbabilityMap:
    def __init__(self, building: Building, cfg: SimConfig, scenario: Scenario, use_cctv: bool = True):
        self.b = building
        self.cfg = cfg
        n = len(building)
        # Start: anyone could be in any room at a low base rate (people no camera saw).
        not_occupied = [1.0 - cfg.base_rate_per_room] * n

        if use_cctv:
            for v in scenario.victims:
                if not v.seen_on_cctv:
                    continue
                # Where we expect the person to be: a little past the last-seen point,
                # in the direction they were walking. Either side of the corridor.
                expect_x = v.last_seen_x + v.heading * cfg.prior_ahead_m
                weights = [
                    math.exp(-((r.door_x - expect_x) ** 2) / (2 * cfg.prior_sigma_m ** 2))
                    for r in building.rooms
                ]
                total = sum(weights)
                for i, w in enumerate(weights):
                    not_occupied[i] *= 1.0 - w / total

        self.p = [1.0 - q for q in not_occupied]

    # --- updates ---------------------------------------------------------------
    def searched_and_empty(self, room: int) -> None:
        """A search found nobody: the room is less likely, but not ruled out (sensors miss)."""
        o = _to_odds(self.p[room]) * (1 - self.cfg.p_thermal_detect)
        self.p[room] = _from_odds(o)

    def searched_and_found(self, room: int) -> None:
        """Someone was found and removed; others may still be there, so treat it like a miss."""
        self.searched_and_empty(room)

    def dog_passed(self, room: int, alerted: bool) -> None:
        c = self.cfg
        if alerted:
            lr = c.p_k9_alert_true / c.p_k9_alert_false
        else:
            lr = (1 - c.p_k9_alert_true) / (1 - c.p_k9_alert_false)
        self.p[room] = _from_odds(_to_odds(self.p[room]) * lr)
