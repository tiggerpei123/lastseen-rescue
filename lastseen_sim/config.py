"""All tunable numbers of the simulation live here, so they are easy to find and argue about.

Every value is an assumption for a simplified model, not a measured field value.
Change one, re-run the benchmark, and see how much the result moves.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimConfig:
    # --- Building -----------------------------------------------------------
    rooms_per_side: int = 8          # rooms on each side of one corridor (16 rooms total)
    room_spacing_m: float = 4.0      # distance between neighbouring doors
    first_door_m: float = 4.0        # distance from the stairwell entry to the first door
    corridor_width_m: float = 2.0    # crossing the corridor to the opposite door

    # --- Search crew (one pair of firefighters moving together, plus a dog) --
    move_speed_mps: float = 0.5      # crawling / searching pace in heavy smoke
    room_search_s: float = 40.0      # time to search one room by hand and thermal camera
    time_limit_s: float = 1200.0     # stop after 20 minutes of search

    # --- Trapped occupants ---------------------------------------------------
    min_victims: int = 2
    max_victims: int = 5

    # --- Pre-fire CCTV (corridor cameras only) --------------------------------
    p_seen_on_cctv: float = 0.6      # share of occupants who passed a corridor camera before smoke
    seen_before_door_max_m: float = 6.0   # last seen up to this far before reaching their door
    cctv_position_noise_m: float = 1.0    # error of the position estimate from video
    p_heading_correct: float = 0.85       # how often the walking direction is read correctly
    prior_ahead_m: float = 3.0            # map assumes the person went this far past the last-seen point
    prior_sigma_m: float = 3.0            # spread of that guess

    # --- Unknown occupants -----------------------------------------------------
    base_rate_per_room: float = 0.08  # prior chance any room holds someone no camera saw

    # --- Sensors ---------------------------------------------------------------
    p_thermal_detect: float = 0.85    # chance a room search finds a person who is there
    p_k9_alert_true: float = 0.6      # dog alerts when passing a door with a person behind it
    p_k9_alert_false: float = 0.05    # dog alerts at an empty room
