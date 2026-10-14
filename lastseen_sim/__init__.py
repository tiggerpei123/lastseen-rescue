"""LastSeen search simulator: compares search strategies for trapped occupants in smoke."""

from .building import Building, Room
from .config import SimConfig
from .probability_map import ProbabilityMap
from .scenario import Scenario, Victim, make_scenario
from .simulate import STRATEGIES, SearchResult, run_search

__all__ = [
    "Building", "Room", "SimConfig", "ProbabilityMap", "Scenario", "Victim",
    "make_scenario", "STRATEGIES", "SearchResult", "run_search",
]
