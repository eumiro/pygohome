"""
Your world.

It consists of tracks, points of interest, intersections,
and a graph that will tell you how to get from A to B.
"""

import datetime as dt
import math
from typing import Dict, List, Tuple

import networkx as nx
import numpy as np

from pygohome.convert import extract_gpx
from pygohome.processor import (
    build_graph,
    find_encounters,
    prepare_trackpoints,
    prepare_waypoints,
    RegionTooLargeError,
)


class World:
    """Your world."""

    trackpoints: List[Tuple[dt.datetime, float, float]]
    waypoints: List[Tuple[str, float, float]]
    graph: nx.DiGraph

    def __init__(self) -> None:
        """Init an empty world."""
        self.trackpoints = []
        self.waypoints = []
        self.graph = None

    def add_trackpoints(self, trackpoints: List) -> None:
        """Add a list of trackpoints."""
        self.trackpoints.extend(trackpoints)
        self.graph = None

    def add_waypoints(self, waypoints: List) -> None:
        """Add a list of waypoints."""
        self.waypoints.extend(waypoints)
        self.graph = None

    def add_gpx(self, track_xml: str) -> None:
        """Add a GPX XML file content."""
        trackpoints, waypoints = extract_gpx(track_xml)
        if trackpoints:
            self.add_trackpoints(trackpoints)
        if waypoints:
            self.add_waypoints(waypoints)

    def _ensure_graph(self) -> None:
        """Rebuild graph if needed."""
        if self.graph is None:
            dfr_trackpoints = prepare_trackpoints(self.trackpoints)
            dfr_waypoints = prepare_waypoints(self.waypoints)
            if set(dfr_trackpoints["utm_zone"]) != set(dfr_waypoints["utm_zone"]):
                raise RegionTooLargeError(
                    f"Trackpoints ({dfr_trackpoints['utm_zone']!r}) and "
                    f"waypoints ({dfr_waypoints['utm_zone']!r}) "
                    f"in different UTM_zones."
                )
            dfr_encounters = find_encounters(dfr_trackpoints, dfr_waypoints)
            self.graph = build_graph(dfr_encounters, dfr_waypoints)

    def fastest_path(self, src: str, dst: str, quantile: float = 0.8) -> nx.Graph:
        """Find the shortest path between src and dst with quantile probability."""
        self._ensure_graph()
        path = nx.path_graph(
            nx.dijkstra_path(
                self.graph, src, dst, lambda u, v, a: np.quantile(a["secs"], quantile)
            )
        )
        return path

    def single_source_periods(self, src: str, quantile: float = 0.8) -> Dict:
        """Return periods to every other waypoint from the src."""
        self._ensure_graph()
        all_dsts_periods = nx.single_source_dijkstra(
            self.graph,
            src,
            weight=lambda u, v, a: int(np.quantile(a["secs"], quantile)),
        )[0]
        periods: Dict = {}
        for dst, period in all_dsts_periods.items():
            if isinstance(dst, tuple):
                # if dst is a tuple(here, src, dst), it is at a lights intersection
                # we want only to get to any node within this intersection
                # result: the shortest period to get to any node near here
                periods[dst[0]] = min(period, periods.get(dst[0], math.inf))
            else:
                periods[dst] = period
        return periods
