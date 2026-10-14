"""Random fire scenarios: where people are trapped, and what the CCTV saw before the smoke."""

import random
from dataclasses import dataclass

from .building import Building
from .config import SimConfig


@dataclass
class Victim:
    vid: int
    room: int                          # index of the room the person is trapped in
    seen_on_cctv: bool
    last_seen_x: float | None = None   # corridor position from the last CCTV frame
    heading: int | None = None         # +1 = walking away from the entry, -1 = towards it


@dataclass
class Scenario:
    seed: int
    victims: list[Victim]


def make_scenario(building: Building, cfg: SimConfig, seed: int) -> Scenario:
    rng = random.Random(seed)
    n = rng.randint(cfg.min_victims, cfg.max_victims)
    victims = []
    for vid in range(n):
        room = rng.randrange(len(building))
        door_x = building.rooms[room].door_x
        v = Victim(vid=vid, room=room, seen_on_cctv=rng.random() < cfg.p_seen_on_cctv)
        if v.seen_on_cctv:
            # The person walked along the corridor towards their door and was last
            # caught on camera a few metres before reaching it.
            true_heading = rng.choice((+1, -1))
            before = rng.uniform(0.0, cfg.seen_before_door_max_m)
            x = door_x - true_heading * before + rng.gauss(0.0, cfg.cctv_position_noise_m)
            v.last_seen_x = x
            v.heading = true_heading if rng.random() < cfg.p_heading_correct else -true_heading
        victims.append(v)
    return Scenario(seed=seed, victims=victims)
