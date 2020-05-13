"""
Your world.

It consists of tracks, points of interest, intersections,
and a graph that will tell you how to get from A to B.
"""

from typing import List, Tuple

from pygohome.convert import gpx_to_trackpoints


class World:
    """Your world."""

    _trackpoints: List[Tuple]
    _checked: bool

    def __init__(self) -> None:
        """Init an empty world."""
        self._trackpoints = []
        self._checked = False

    def add_trackpoints(self, trackpoints: List) -> None:
        """Add a list of trackpoints."""
        self._trackpoints.extend(trackpoints)
        self._checked = False

    def add_gpx(self, track_xml: str) -> None:
        """Add a GPX XML file content."""
        trackpoints = gpx_to_trackpoints(track_xml)
        self.add_trackpoints(trackpoints)
