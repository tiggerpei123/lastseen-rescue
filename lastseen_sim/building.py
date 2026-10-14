"""A one-floor building: a straight corridor with rooms on both sides.

    entry  201  202  203  ...  208        <- north side
    ==>  ------------------------------    <- corridor (x measured in metres from the entry)
           209  210  211  ...  216        <- south side
"""

from dataclasses import dataclass

from .config import SimConfig


@dataclass(frozen=True)
class Room:
    index: int      # 0 .. n-1, used internally
    name: str       # label shown on maps, e.g. "203"
    door_x: float   # position of the door along the corridor, in metres
    side: str       # "N" (north) or "S" (south)


class Building:
    def __init__(self, cfg: SimConfig):
        self.cfg = cfg
        self.rooms: list[Room] = []
        for side_i, side in enumerate(("N", "S")):
            for k in range(cfg.rooms_per_side):
                idx = side_i * cfg.rooms_per_side + k
                self.rooms.append(
                    Room(
                        index=idx,
                        name=str(201 + idx),
                        door_x=cfg.first_door_m + k * cfg.room_spacing_m,
                        side=side,
                    )
                )

    def __len__(self) -> int:
        return len(self.rooms)

    def travel_time(self, from_x: float, from_side: str | None, room: Room) -> float:
        """Seconds to move from a point in the corridor to a room's door."""
        dist = abs(room.door_x - from_x)
        if from_side is not None and from_side != room.side:
            dist += self.cfg.corridor_width_m
        return dist / self.cfg.move_speed_mps

    def doors_passed(self, from_x: float, to_x: float) -> list[Room]:
        """Doors the crew (and the dog) walk past on the way, including the destination."""
        lo, hi = sorted((from_x, to_x))
        return [r for r in self.rooms if lo <= r.door_x <= hi]
